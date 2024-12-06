mod genetic;
mod manager;

use csv::ReaderBuilder;
use genetic::GeneticSolver;
use manager::PackageManager;
use rand::Rng;
use serde::{Deserialize, Serialize};
use std::fs::File;
use std::{collections::HashMap, thread, time};

use genetic::Package;
use genetic::ULD;

#[derive(Debug, Serialize, Deserialize)]
pub struct Request {
    packages: Vec<Package>,
    ulds: Vec<ULD>,
    mock: bool, //TODO: initialize this field with true
}

impl Request {
    pub fn new(packages: Vec<Package>, ulds: Vec<ULD>) -> Request {
        let mock = true;
        Request {
            packages,
            ulds,
            mock,
        }
    }
}

#[derive(Debug, Serialize, Deserialize)]
pub struct Solution {
    uld_order: Vec<usize>,
    pack_order: Vec<usize>,
    alloted: Vec<Package>,
}

pub fn get_cached_solution() -> Vec<HashMap<String, String>> {
    let file = File::open("sample_solution.csv").expect("Unable to open file");
    let mut rdr = ReaderBuilder::new().has_headers(true).from_reader(file);

    let mut result = Vec::new();
    for record in rdr.records() {
        let record = record.expect("Unable to read record");
        let mut record_map = HashMap::new();
        for (i, field) in record.iter().enumerate() {
            record_map.insert(format!("column_{}", i), field.to_string());
        }
        result.push(record_map);
    }
    result
}

pub fn generate_solution(req: Request) -> Vec<String> {
    if req.mock {
        let delay = rand::thread_rng().gen_range(0.2..1.5);
        thread::sleep(time::Duration::from_secs_f64(delay));

        return get_cached_solution()
            .into_iter()
            .map(|record| serde_json::to_string(&record).expect("Unable to serialize record"))
            .collect();
    }

    let mut solver = GeneticSolver::new(req.packages.clone(), req.ulds.clone(), 2, 500, 1, 0.8);
    let base_solution = solver.run();

    let mut mng = PackageManager::new(
        req.packages.len(),
        req.ulds.len(),
        base_solution.uld_order,
        base_solution.pack_order,
        base_solution.alloted,
    );

    mng.get_results()
}
