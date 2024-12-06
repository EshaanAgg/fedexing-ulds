use std::collections::HashSet;

use super::genetic::Package;

#[derive(Debug)]
pub struct PackageManager {
    num_of_total_pkgs: usize,
    num_of_ulds: usize,
    uld_order: Vec<usize>,
    lis_u: Vec<(usize, f64, f64, f64)>,
    sol: Vec<(usize, usize, f64, f64, f64, f64, f64, f64)>,
    adj_lis: Vec<Vec<usize>>,
    available: Vec<bool>,
    find_pack: Vec<(bool, Option<usize>)>,
    uld_wise: Vec<Vec<(usize, usize, f64, f64, f64, f64, f64, f64)>>,
    package_wise_data: Vec<Option<(usize, usize, f64, f64, f64, f64, f64, f64)>>,
    in_deg: Vec<usize>,
    visited: Vec<bool>,
    final_order: Vec<String>,
}

impl PackageManager {
    pub fn new(
        num_of_total_pkgs: usize,
        num_of_ulds: usize,
        uld_order: Vec<usize>,
        lis_u: Vec<usize>,
        sol: Vec<Package>,
    ) -> Self {
        // Convert lis_u to the expected type
        let lis_u_converted: Vec<(usize, f64, f64, f64)> = lis_u
            .into_iter()
            .map(|u| (u, 0.0, 0.0, 0.0)) // Assuming default values for f64 fields
            .collect();

        // Convert sol to the expected type
        let sol_converted: Vec<(usize, usize, f64, f64, f64, f64, f64, f64)> = sol
            .into_iter()
            .map(|p| {
                (
                    p.id.parse::<usize>().unwrap(), p.length as usize, p.length as f64, p.width as f64, p.height as f64, p.weight as f64, 0.0, 0.0,
                )
            }) // Assuming Package struct has these fields
            .collect();

        Self {
            num_of_total_pkgs,
            num_of_ulds,
            uld_order,
            lis_u: lis_u_converted,
            sol: sol_converted,
            adj_lis: vec![vec![]; num_of_total_pkgs],
            available: vec![false; num_of_total_pkgs],
            find_pack: vec![(false, None); num_of_total_pkgs],
            uld_wise: vec![vec![]; num_of_ulds],
            package_wise_data: vec![None; num_of_total_pkgs],
            in_deg: vec![0; num_of_total_pkgs],
            visited: vec![false; num_of_total_pkgs],
            final_order: vec![],
        }
    }

    pub fn group_packages_by_uld(&mut self) {
        for item in &self.sol {
            self.uld_wise[item.1].push(item.clone());
            self.package_wise_data[item.0] = Some(item.clone());
            self.find_pack[item.0] = (true, Some(item.1));
        }
    }

    pub fn check_new(
        &self,
        uid: usize,
        x: f64,
        y: f64,
        z: f64,
        x1: f64,
        y1: f64,
        z1: f64,
        new_res: &Vec<(usize, usize, f64, f64, f64, f64, f64, f64)>,
    ) -> bool {
        if x + x1 > self.lis_u[uid].1 || y + y1 > self.lis_u[uid].2 || z + z1 > self.lis_u[uid].3 {
            return false;
        }

        for ele in new_res {
            if ele.1 == uid
                && self.check_intersection_cuboids(
                    [x, y, z],
                    [x + x1, y + y1, z + z1],
                    [ele.2, ele.3, ele.4],
                    [ele.5, ele.6, ele.7],
                )
            {
                return false;
            }
        }

        true
    }

    pub fn check_intersection_cuboids(
        &self,
        cuboid1_min: [f64; 3],
        cuboid1_max: [f64; 3],
        cuboid2_min: [f64; 3],
        cuboid2_max: [f64; 3],
    ) -> bool {
        for i in 0..3 {
            if cuboid1_max[i] <= cuboid2_min[i] || cuboid2_max[i] <= cuboid1_min[i] {
                return false;
            }
        }
        true
    }

    pub fn find_dependencies(
        &self,
        mut cord: [f64; 3],
        dims: [f64; 3],
        pid: usize,
        uid: usize,
        axis: &str,
    ) -> Vec<usize> {
        let idx = if axis == "x" { 0 } else { 2 };
        let mut dependencies = vec![];

        while cord[idx] > 0.0 {
            cord[idx] -= 1.0;
            for ele in &self.uld_wise[uid] {
                if ele.0 != pid
                    && self.check_intersection_cuboids(
                        cord,
                        [cord[0] + dims[0], cord[1] + dims[1], cord[2] + dims[2]],
                        [ele.2, ele.3, ele.4],
                        [ele.5, ele.6, ele.7],
                    )
                {
                    dependencies.push(ele.0);
                }
            }
        }

        dependencies
            .into_iter()
            .collect::<HashSet<_>>()
            .into_iter()
            .collect()
    }

    pub fn construct_graph(&mut self, pid: usize, uid: usize) {
        self.available[pid] = true;

        let data = self.uld_wise[uid].iter().find(|i| i.0 == pid).cloned();

        if let Some(data) = data {
            let (x, y, z) = (data.2, data.3, data.4);
            let (a, b, c) = (data.5 - x, data.6 - y, data.7 - z);
            let point = [x, y, z];

            let mut dependencies = self.find_dependencies(point, [a, b, c], pid, uid, "x");
            dependencies.extend(self.find_dependencies(point, [a, b, c], pid, uid, "z"));
            dependencies.sort();
            dependencies.dedup();

            self.adj_lis[pid] = dependencies.clone();
            for &dep in &dependencies {
                if !self.available[dep] {
                    self.construct_graph(dep, uid);
                }
            }
        }
    }

    pub fn topo_sort(&mut self) {
        pub fn dfs(pkg_manager: &mut PackageManager, pid: usize) {
            pkg_manager.visited[pid] = true;
            let dependencies = pkg_manager.adj_lis[pid].clone();
            for dep in dependencies {
                if !pkg_manager.visited[dep] {
                    dfs(pkg_manager, dep);
                }
            }
            pkg_manager.final_order.push(pid.to_string());
        }

        let mut pkg_ind: Vec<usize> = (0..self.num_of_total_pkgs).collect();
        pkg_ind.sort_by_key(|&x| self.in_deg[x]);

        for &pid in &pkg_ind {
            if !self.visited[pid] && self.find_pack[pid].0 {
                self.construct_graph(pid, self.find_pack[pid].1.unwrap());
            }
        }

        for &pid in &pkg_ind {
            if !self.visited[pid] {
                dfs(self, pid);
            }
        }
    }

    pub fn get_results(&mut self) -> Vec<String> {
        self.topo_sort();
        self.final_order.clone()
    }
}
