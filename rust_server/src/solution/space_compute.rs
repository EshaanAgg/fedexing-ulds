#![allow(warnings, unused)]

use std::cmp::{max, min};
use std::collections::HashMap;
use std::f64::INFINITY;
use std::fs::File;
use std::io::Write;
use csv::ReaderBuilder;
use serde::Deserialize;

#[derive(Debug, Deserialize)]
pub struct PackageData {
    uld_id: i32,
    pack_id: i32,
    x1: i32,
    y1: i32,
    z1: i32,
    x2: i32,
    y2: i32,
    z2: i32,
}

pub fn compute_space(solution_path: &str, output_path: &str) {
    let mut rdr = ReaderBuilder::new().has_headers(true).from_path(solution_path).unwrap();
    let mut package_data: Vec<PackageData> = Vec::new();

    // Read data into vector
    for result in rdr.deserialize() {
        let record: PackageData = result.unwrap();
        package_data.push(record);
    }

    // Group by uld_id
    let mut grouped_data: HashMap<i32, Vec<&PackageData>> = HashMap::new();
    for package in &package_data {
        grouped_data.entry(package.uld_id).or_insert_with(Vec::new).push(package);
    }

    let mut output_file = File::create(output_path).expect("Unable to create file");

    for (uld_id, group) in &grouped_data {
        let mut tot_volume = 0.0;
        let mut tot_pack_volume = 0.0;

        for row in group {
            let mut nearest_to_f1 = vec![vec![INFINITY; (row.y2 - row.y1 + 1) as usize]; (row.z2 - row.z1 + 1) as usize];
            let mut nearest_to_f2 = vec![vec![INFINITY; (row.y2 - row.y1 + 1) as usize]; (row.z2 - row.z1 + 1) as usize];
            let mut nearest_to_f3 = vec![vec![INFINITY; (row.x2 - row.x1 + 1) as usize]; (row.z2 - row.z1 + 1) as usize];
            let mut nearest_to_f4 = vec![vec![INFINITY; (row.x2 - row.x1 + 1) as usize]; (row.z2 - row.z1 + 1) as usize];

            // Calculate total pack volume
            tot_pack_volume += (row.x2 - row.x1) as f64 * (row.y2 - row.y1) as f64 * (row.z2 - row.z1) as f64;

            for pack2 in group.iter() {
                if pack2.pack_id == row.pack_id {
                    continue;
                }

                let min_x = max(row.x1, pack2.x1);
                let max_x = min(row.x2, pack2.x2);
                let min_y = max(row.y1, pack2.y1);
                let max_y = min(row.y2, pack2.y2);
                let min_z = max(row.z1, pack2.z1);
                let max_z = min(row.z2, pack2.z2);

                // Updating nearest_to_f1, nearest_to_f2, nearest_to_f3, nearest_to_f4
                for y in min_y..=max_y {
                    for z in min_z..=max_z {
                        if pack2.x2 <= row.x1 {
                            nearest_to_f1[(z - row.z1) as usize][(y - row.y1) as usize] =
                                nearest_to_f1[(z - row.z1) as usize][(y - row.y1) as usize].min(row.x1 as f64 - pack2.x2 as f64);
                        } else if pack2.x1 >= row.x2 {
                            nearest_to_f2[(z - row.z1) as usize][(y - row.y1) as usize] =
                                nearest_to_f2[(z - row.z1) as usize][(y - row.y1) as usize].min(pack2.x1 as f64 - row.x2 as f64);
                        }
                    }
                }

                for x in min_x..=max_x {
                    for z in min_z..=max_z {
                        if pack2.y2 <= row.y1 {
                            nearest_to_f3[(z - row.z1) as usize][(x - row.x1) as usize] =
                                nearest_to_f3[(z - row.z1) as usize][(x - row.x1) as usize].min(row.y1 as f64 - pack2.y2 as f64);
                        } else if pack2.y1 >= row.y2 {
                            nearest_to_f4[(z - row.z1) as usize][(x - row.x1) as usize] =
                                nearest_to_f4[(z - row.z1) as usize][(x - row.x1) as usize].min(pack2.y1 as f64 - row.y2 as f64);
                        }
                    }
                }
            }

            // Calculate total volume for nearest_to_f1 and nearest_to_f2
            for y in row.y1..=row.y2 {
                for z in row.z1..=row.z2 {
                    let idx1 = (y - row.y1) as usize;
                    let idx2 = (z - row.z1) as usize;
                    if nearest_to_f1[idx2][idx1] != INFINITY {
                        tot_volume += nearest_to_f1[idx2][idx1];
                    }
                    if nearest_to_f2[idx2][idx1] != INFINITY {
                        tot_volume += nearest_to_f2[idx2][idx1];
                    }
                }
            }

            // Calculate total volume for nearest_to_f3 and nearest_to_f4
            for x in row.x1..=row.x2 {
                for z in row.z1..=row.z2 {
                    let idx1 = (x - row.x1) as usize;
                    let idx2 = (z - row.z1) as usize;
                    if nearest_to_f3[idx2][idx1] != INFINITY {
                        tot_volume += nearest_to_f3[idx2][idx1];
                    }
                    if nearest_to_f4[idx2][idx1] != INFINITY {
                        tot_volume += nearest_to_f4[idx2][idx1];
                    }
                }
            }
        }

        tot_volume /= 2.0;
        let output = format!(
            "ULD ID: {} | Cushion Vol: {} | Total pack volume: {} | Frac: {}\n",
            uld_id,
            tot_volume,
            tot_pack_volume,
            tot_volume / tot_pack_volume
        );
        println!("{}", output);
        output_file.write_all(output.as_bytes()).expect("Unable to write data");
    }
}