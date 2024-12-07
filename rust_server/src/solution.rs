#![allow(warnings, unused)]

mod genetic;
mod manager;
mod space_compute;

use genetic::GeneticSolver;
use manager::PackageManager;
use rand::Rng;
use serde::{Deserialize, Serialize};
use space_compute::compute_space;
use std::{thread, time};

use genetic::Package;
use genetic::ULD;

#[derive(Debug, Serialize, Deserialize)]
pub struct Request {
    packages: Vec<Package>,
    ulds: Vec<ULD>,
    mock: Option<bool>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct Solution {
    uld_order: Vec<usize>,
    pack_order: Vec<usize>,
    alloted: Vec<Package>,
}

#[derive(Debug, Serialize, Deserialize, Eq, PartialEq)]
pub struct SolutionRow {
    pack_id: String,
    uld_id: String,
    x1: i32,
    x2: i32,
    y1: i32,
    y2: i32,
    z1: i32,
    z2: i32,
}

pub fn get_cached_solution() -> Vec<SolutionRow> {
    let data = std::fs::read_to_string("./sample_solution.csv").expect("Unable to read file");
    let mut rdr = csv::Reader::from_reader(data.as_bytes());
    let mut iter = rdr.deserialize();

    let mut parsed_rows: Vec<SolutionRow> = Vec::new();
    while let Some(result) = iter.next() {
        let record: SolutionRow = result.expect("Unable to parse record");
        parsed_rows.push(record);
    }

    parsed_rows
}

pub fn generate_solution(req: Request) -> Vec<SolutionRow> {
    if req.mock.unwrap_or(true) {
        let delay = rand::thread_rng().gen_range(0.2..1.5);
        thread::sleep(time::Duration::from_secs_f64(delay));

        return get_cached_solution();
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

    compute_space("./data/solution.csv", "./data/soln_for_viz.csv");
    mng.get_results()
}
