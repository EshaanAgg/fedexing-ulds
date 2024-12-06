use rand::Rng;
use serde::{Deserialize, Serialize};
use std::cmp::{max, min, Ordering};
use std::collections::{HashMap, HashSet};
use std::fs::File;
use std::io::Write;

use super::Solution;

const PENALTY_COST: i32 = 10_000_000;
const COST_PER_ULD: i32 = 5_000;

// Utility function to check intersection of cuboids
pub fn check_intersection_cuboids(a0: [i32; 3], a1: [i32; 3], b0: [i32; 3], b1: [i32; 3]) -> bool {
    let dx = min(a1[0], b1[0]) - max(a0[0], b0[0]);
    let dy = min(a1[1], b1[1]) - max(a0[1], b0[1]);
    let dz = min(a1[2], b1[2]) - max(a0[2], b0[2]);
    dx > 0 && dy > 0 && dz > 0
}

// Directions as a global constant
const DIRECTS: [[i32; 3]; 9] = [
    [0, 0, 0],
    [0, 0, 0],
    [0, -1, 0],
    [-1, 0, 0],
    [-1, -1, 0],
    [0, 0, -1],
    [0, -1, -1],
    [-1, 0, -1],
    [-1, -1, -1],
];

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct Package {
    pub id: String,
    pub length: f32,
    pub width: f32,
    pub height: f32,
    pub weight: f32,
    pub cost: f32,
    pub priority: bool,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct ULD {
    id: String,
    length: f32,
    width: f32,
    height: f32,
    weight: f32,
}

impl ULD {
    pub fn capacity(&self) -> f32 {
        self.weight
    }
}

// Config pub struct with implementation
#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct Config {
    pub priority_order: Vec<usize>,
    pub non_priority_order: Vec<usize>,
    pub enc_priority_ord: Vec<f64>,
    pub enc_non_priority_ord: Vec<f64>,
    pub fitness_score: i32,
    pub packages_placed: usize,
    pub resultant_data: Vec<(usize, usize, i32, i32, i32, i32, i32, i32)>,
    pub priority_packed: usize,
    pub non_priority_packed: usize,
    pub ulds_used_for_priority: usize,
    pub evaluated: bool,
    pub uld_wts: Vec<i32>,
    pub all_pkgs: Vec<Package>,
    pub all_ulds: Vec<ULD>,
    pub count_priority_pkg: usize,
    pub count_non_priority_pkg: usize,
    pub priority_idx: Vec<usize>,
    pub non_priority_idx: Vec<usize>,
    pub tot: f32,
}

impl Config {
    pub fn new(all_pkgs: Vec<Package>, all_ulds: Vec<ULD>) -> Self {
        let count_priority_pkg = all_pkgs.iter().filter(|pkg| pkg.priority).count();
        let count_non_priority_pkg = all_pkgs.len() - count_priority_pkg;
        let priority_idx = all_pkgs
            .iter()
            .enumerate()
            .filter_map(|(i, pkg)| if pkg.priority { Some(i) } else { None })
            .collect();
        let non_priority_idx = all_pkgs
            .iter()
            .enumerate()
            .filter_map(|(i, pkg)| if !pkg.priority { Some(i) } else { None })
            .collect();
        let uld_wts = vec![0; all_ulds.len()];

        Self {
            priority_order: Vec::new(),
            non_priority_order: Vec::new(),
            enc_priority_ord: Vec::new(),
            enc_non_priority_ord: Vec::new(),
            fitness_score: -1,
            packages_placed: 0,
            resultant_data: Vec::new(),
            priority_packed: 0,
            non_priority_packed: 0,
            ulds_used_for_priority: 0,
            evaluated: false,
            uld_wts,
            all_pkgs,
            all_ulds,
            count_priority_pkg,
            count_non_priority_pkg,
            priority_idx,
            non_priority_idx,
            tot: 0.0,
        }
    }

    pub fn initialize(&mut self) {
        let mut rng = rand::thread_rng();
        self.enc_priority_ord = (0..self.count_priority_pkg)
            .map(|_| rng.gen_range(0.0..1.0))
            .collect();
        self.enc_non_priority_ord = (0..self.count_non_priority_pkg)
            .map(|_| rng.gen_range(0.0..1.0))
            .collect();
    }

    pub fn decode(&mut self) {
        let mut relative_p_order: Vec<_> = self.enc_priority_ord.iter().enumerate().collect();
        let mut relative_non_p_order: Vec<_> =
            self.enc_non_priority_ord.iter().enumerate().collect();

        relative_p_order.sort_by(|a, b| a.1.partial_cmp(b.1).unwrap());
        relative_non_p_order.sort_by(|a, b| a.1.partial_cmp(b.1).unwrap());

        self.priority_order = relative_p_order
            .iter()
            .map(|(i, _)| self.priority_idx[*i])
            .collect();
        self.non_priority_order = relative_non_p_order
            .iter()
            .map(|(i, _)| self.non_priority_idx[*i])
            .collect();
    }

    pub fn reset_uld_points(&self) -> Vec<Vec<Vec<i32>>> {
        let mut uld_pts: Vec<Vec<Vec<i32>>> = vec![vec![]; self.all_ulds.len()];

        for obj in &self.resultant_data {
            let (_, uid, x1, y1, z1, x2, y2, z2) = *obj;
            let uid = uid as usize;
            let a = x2 - x1;
            let b = y2 - y1;
            let c = z2 - z1;
            let x = x1;
            let y = y1;
            let z = z1;

            let args = [
                [0, 0, 0],
                [a, 0, 0],
                [0, b, 0],
                [0, 0, c],
                [a, b, 0],
                [a, 0, c],
                [0, b, c],
                [a, b, c],
            ];

            for (i, num) in (1..=8).enumerate() {
                for j in 0..8 {
                    uld_pts[uid].push(vec![
                        x + args[j][0],
                        y + args[j][1],
                        z + args[j][2],
                        num as i32,
                    ]);
                }
            }
        }

        for uld in &self.all_ulds {
            let uid = self.all_ulds.iter().position(|u| u.id == uld.id).unwrap();
            uld_pts[uid].extend(vec![
                vec![0, 0, 0, 1],
                vec![uld.length as i32, 0, 0, 3],
                vec![0, uld.width as i32, 0, 2],
                vec![uld.length as i32, uld.width as i32, 0, 4],
                vec![0, 0, uld.height as i32, 5],
                vec![uld.length as i32, 0, uld.height as i32, 7],
                vec![0, uld.width as i32, uld.height as i32, 6],
                vec![uld.length as i32, uld.width as i32, uld.height as i32, 8],
            ]);
        }

        uld_pts
    }

    pub fn sort_criteria(
        &self,
        a: &(usize, String, i32, i32, i32, f32, f32, f32, i32),
        b: &(usize, String, i32, i32, i32, f32, f32, f32, i32),
        uld_pts: &Vec<[i32; 4]>,
        capacity: f32,
        uld_wt: i32,
    ) -> Ordering {
        let len_a = uld_pts.len();
        let len_b = uld_pts.len();
        let (_, uld_id_a, x_a, y_a, _, length_a, width_a, _, _) = a;
        let (_, uld_id_b, x_b, y_b, _, length_b, width_b, _, _) = b;

        len_b
            .cmp(&len_a)
            .then_with(|| a.4.partial_cmp(&b.4).unwrap_or(Ordering::Equal))
            .then_with(|| {
                let a_dist = i32::abs(
                    i32::min(
                        *x_a,
                        self.all_ulds
                            .iter()
                            .find(|u| u.id == *uld_id_a)
                            .unwrap()
                            .length as i32
                            - *x_a
                            - *length_a as i32,
                    ) + i32::min(
                        *y_a,
                        self.all_ulds
                            .iter()
                            .find(|u| u.id == *uld_id_a)
                            .unwrap()
                            .width as i32
                            - *y_a
                            - *width_a as i32,
                    ),
                );
                let b_dist = i32::abs(
                    i32::min(
                        *x_b,
                        self.all_ulds
                            .iter()
                            .find(|u| u.id == *uld_id_b)
                            .unwrap()
                            .length as i32
                            - *x_b
                            - *length_b as i32,
                    ) + i32::min(
                        *y_b,
                        self.all_ulds
                            .iter()
                            .find(|u| u.id == *uld_id_b)
                            .unwrap()
                            .width as i32
                            - *y_b
                            - *width_b as i32,
                    ),
                );

                a_dist.cmp(&b_dist)
            })
            .then_with(|| {
                let (_, _, ax, ay, az, _, _, _, _) = a;
                let (_, _, bx, by, bz, _, _, _, _) = b;
                let a_sum = ax * ax + ay * ay + az * az;
                let b_sum = bx * bx + by * by + bz * bz;

                a_sum.cmp(&b_sum)
            })
    }

    pub fn add_point(
        &self,
        uid: String,
        x: i32,
        y: i32,
        z: i32,
        a: i32,
        b: i32,
        c: i32,
        uld_pts: &mut HashMap<String, Vec<[i32; 4]>>,
    ) {
        let args = [
            [0, 0, 0],
            [a, 0, 0],
            [0, b, 0],
            [0, 0, c],
            [a, b, 0],
            [a, 0, c],
            [0, b, c],
            [a, b, c],
        ];

        for (i, num) in (1..=8).enumerate() {
            if let Some(pts) = uld_pts.get_mut(&uid) {
                for j in 0..8 {
                    pts.push([x + args[j][0], y + args[j][1], z + args[j][2], num as i32]);
                }
            }
        }
    }

    pub fn final_checker(
        &self,
        uid: usize,
        pt_of_place: &[i32; 3],
        orientation: &[i32; 3],
        pid: usize,
    ) -> bool {
        let uld = &self.all_ulds[uid];
        let pkg = &self.all_pkgs[pid];

        // Check if the package weight exceeds the ULD weight limit
        if self.uld_wts[uid] + pkg.weight as i32 > uld.weight as i32 {
            return false;
        }

        // Check if the package dimensions exceed the ULD dimensions
        if pt_of_place[0] + orientation[0] > uld.length as i32
            || pt_of_place[1] + orientation[1] > uld.width as i32
            || pt_of_place[2] + orientation[2] > uld.height as i32
        {
            return false;
        }

        // Check for intersections with already placed packages
        for ele in &self.resultant_data {
            let (_, ele_uid, ex1, ey1, ez1, ex2, ey2, ez2) = *ele;
            if ele_uid == uid as usize {
                let second_pt = [
                    pt_of_place[0] + orientation[0],
                    pt_of_place[1] + orientation[1],
                    pt_of_place[2] + orientation[2],
                ];
                if check_intersection_cuboids(
                    *pt_of_place,
                    second_pt,
                    [ex1, ey1, ez1],
                    [ex2, ey2, ez2],
                ) {
                    return false;
                }
            }
        }

        true
    }

    pub fn place_priority(&mut self, uld_pts: &mut HashMap<String, Vec<[i32; 4]>>) {
        let directs = DIRECTS;

        for &pid in &self.priority_order {
            let pckg = &self.all_pkgs[pid];
            let mut poss_pts = Vec::new();

            let orientations = vec![
                [pckg.length, pckg.width, pckg.height],
                [pckg.length, pckg.height, pckg.width],
                [pckg.width, pckg.length, pckg.height],
                [pckg.width, pckg.height, pckg.length],
                [pckg.height, pckg.length, pckg.width],
                [pckg.height, pckg.width, pckg.length],
            ];

            for uld in &self.all_ulds {
                if let Some(ref_pts) = uld_pts.get(&uld.id) {
                    for ref_pt in ref_pts {
                        let [x, y, z, dir_idx] = *ref_pt;

                        for orient in &orientations {
                            let xx = x + (orient[0] as i32) * directs[dir_idx as usize][0];
                            let yy = y + orient[1] as i32 * directs[dir_idx as usize][1];
                            let zz = z + orient[2] as i32 * directs[dir_idx as usize][2];

                            if xx < 0 || yy < 0 || zz < 0 {
                                continue;
                            }

                            if self.final_checker(
                                self.all_ulds.iter().position(|u| u.id == uld.id).unwrap(),
                                &[xx, yy, zz],
                                &[orient[0] as i32, orient[1] as i32, orient[2] as i32],
                                pid,
                            ) {
                                poss_pts.push((
                                    pid,
                                    uld.id.clone(),
                                    xx,
                                    yy,
                                    zz,
                                    orient[0],
                                    orient[1],
                                    orient[2],
                                    dir_idx,
                                ));
                            }
                        }
                    }
                }
            }

            poss_pts.sort_by(|a, b| {
                let (_, uld_id_a, _, _, z_a, _, _, _, _) = a;
                let (_, uld_id_b, _, _, z_b, _, _, _, _) = b;

                let len_a = uld_pts[uld_id_a].len();
                let len_b = uld_pts[uld_id_b].len();

                len_b
                    .cmp(&len_a)
                    .then_with(|| z_a.cmp(z_b))
                    .then_with(|| {
                        let a_dist = i32::abs(
                            i32::min(
                                a.2,
                                self.all_ulds.iter().find(|u| u.id == a.1).unwrap().length as i32
                                    - a.2
                                    - a.5 as i32,
                            ) + i32::min(
                                a.3,
                                self.all_ulds.iter().find(|u| u.id == a.1).unwrap().width as i32
                                    - a.3
                                    - a.6 as i32,
                            ),
                        );
                        let b_dist = i32::abs(
                            i32::min(
                                b.2,
                                self.all_ulds.iter().find(|u| u.id == b.1).unwrap().length as i32
                                    - b.2
                                    - b.5 as i32,
                            ) + i32::min(
                                b.3,
                                self.all_ulds.iter().find(|u| u.id == b.1).unwrap().width as i32
                                    - b.3
                                    - b.6 as i32,
                            ),
                        );

                        a_dist.cmp(&b_dist)
                    })
                    .then_with(|| {
                        let a_sum = a.2 * a.2 + a.3 * a.3 + a.4 * a.4;
                        let b_sum = b.2 * b.2 + b.3 * b.3 + b.4 * b.4;

                        a_sum.cmp(&b_sum)
                    })
            });

            if let Some(best_pt) = poss_pts.first() {
                let (pid, uld_id, xx, yy, zz, l, w, h, dir_idx) = best_pt;

                self.resultant_data.push((
                    *pid,
                    self.all_ulds.iter().position(|u| u.id == *uld_id).unwrap(),
                    *xx,
                    *yy,
                    *zz,
                    *xx + *l as i32,
                    *yy + *w as i32,
                    *zz + *h as i32,
                ));

                self.uld_wts[self.all_ulds.iter().position(|u| u.id == *uld_id).unwrap()] +=
                    pckg.weight as i32;

                let x_t = *xx - *l as i32 * directs[*dir_idx as usize][0];
                let y_t = *yy - *w as i32 * directs[*dir_idx as usize][1];
                let z_t = *zz - *h as i32 * directs[*dir_idx as usize][2];

                if let Some(points) = uld_pts.get_mut(uld_id) {
                    points.retain(|pt| {
                        pt[0] != x_t || pt[1] != y_t || pt[2] != z_t || pt[3] != *dir_idx
                    });

                    self.add_point(
                        uld_id.to_string(),
                        x_t as i32,
                        y_t as i32,
                        z_t as i32,
                        *l as i32,
                        *w as i32,
                        *h as i32,
                        uld_pts,
                    );
                }
            }
        }
    }

    pub fn update_resultant_data(&mut self, best_pt: &Vec<usize>) {
        let (pid, uld_id, xx, yy, zz, l, w, h, dir_idx) = (
            best_pt[0], best_pt[1], best_pt[2], best_pt[3], best_pt[4], best_pt[5], best_pt[6],
            best_pt[7], best_pt[8],
        );

        self.resultant_data.push((
            pid,
            uld_id,
            xx.try_into().unwrap(),
            yy.try_into().unwrap(),
            zz.try_into().unwrap(),
            (xx + l as usize).try_into().unwrap(),
            (yy + w as usize).try_into().unwrap(),
            (zz + h as usize).try_into().unwrap(),
        ));

        self.uld_wts[uld_id] += self.all_pkgs[pid].weight as i32;
    }

    pub fn add_reference_points(
        &self,
        uld_pts: &mut HashMap<String, Vec<[i32; 4]>>,
        best_pt: &Vec<usize>,
    ) {
        let (pid, uld_id, xx, yy, zz, l, w, h, dir_idx) = (
            best_pt[0], best_pt[1], best_pt[2], best_pt[3], best_pt[4], best_pt[5], best_pt[6],
            best_pt[7], best_pt[8],
        );

        let x_t = xx - l * DIRECTS[dir_idx as usize][0] as usize;
        let y_t = yy - w * DIRECTS[dir_idx][1] as usize;
        let z_t = zz - h * DIRECTS[dir_idx][2] as usize;

        if let Some(points) = uld_pts.get_mut(&self.all_ulds[uld_id].id) {
            points.retain(|pt| {
                pt[0] != x_t as i32
                    || pt[1] != y_t as i32
                    || pt[2] != z_t as i32
                    || pt[3] != dir_idx as i32
            });

            self.add_point(
                self.all_ulds[uld_id].id.clone(),
                x_t as i32,
                y_t as i32,
                z_t as i32,
                l as i32,
                w as i32,
                h as i32,
                uld_pts,
            );
        }
    }

    pub fn place_economy(&mut self, uld_pts: &mut HashMap<String, Vec<[i32; 4]>>) {
        let non_priority_order = self.non_priority_order.clone();
        for pid in &non_priority_order {
            let pckg = &self.all_pkgs[*pid];
            let mut poss_pts = Vec::new();
            let orientations = [
                [pckg.length, pckg.width, pckg.height],
                [pckg.length, pckg.height, pckg.width],
                [pckg.width, pckg.length, pckg.height],
                [pckg.width, pckg.height, pckg.length],
                [pckg.height, pckg.length, pckg.width],
                [pckg.height, pckg.width, pckg.length],
            ];

            for uid in &self.all_ulds {
                if let Some(ref_pts) = uld_pts.get_mut(&uid.id) {
                    for ref_pt in ref_pts.iter() {
                        let (mut xx, mut yy, mut zz) = (ref_pt[0], ref_pt[1], ref_pt[2]);
                        let dir_idx = ref_pt[3];

                        for args in &orientations {
                            xx = ref_pt[0] + args[0] as i32 * DIRECTS[dir_idx as usize][0];
                            yy = ref_pt[1] + args[1] as i32 * DIRECTS[dir_idx as usize][1];
                            zz = ref_pt[2] + args[2] as i32 * DIRECTS[dir_idx as usize][2];

                            if xx < 0 || yy < 0 || zz < 0 {
                                continue;
                            }

                            if self.final_checker(
                                self.all_ulds.iter().position(|u| u.id == uid.id).unwrap(),
                                &[xx, yy, zz],
                                &[args[0] as i32, args[1] as i32, args[2] as i32],
                                *pid,
                            ) {
                                poss_pts.push(vec![
                                    *pid,
                                    self.all_ulds.iter().position(|u| u.id == uid.id).unwrap(),
                                    xx.try_into().unwrap(),
                                    yy.try_into().unwrap(),
                                    zz.try_into().unwrap(),
                                    args[0] as usize,
                                    args[1] as usize,
                                    args[2] as usize,
                                    dir_idx as usize,
                                ]);
                            }
                        }
                    }
                }
            }

            poss_pts.sort_by(|a, b| {
                self.sort_criteria(
                    &(
                        a[0],
                        self.all_ulds[a[1]].id.clone(),
                        a[2] as i32,
                        a[3] as i32,
                        a[4] as i32,
                        a[5] as f32,
                        a[6] as f32,
                        a[7] as f32,
                        a[8] as i32,
                    ),
                    &(
                        b[0],
                        self.all_ulds[b[1]].id.clone(),
                        b[2] as i32,
                        b[3] as i32,
                        b[4] as i32,
                        b[5] as f32,
                        b[6] as f32,
                        b[7] as f32,
                        b[8] as i32,
                    ),
                    &uld_pts[&self.all_ulds[a[1]].id],
                    self.all_ulds[a[1]].capacity(),
                    self.uld_wts[a[1]],
                )
            });

            if let Some(best_pt) = poss_pts.get(0) {
                let best_pt_clone = best_pt.clone();
                self.update_resultant_data(&best_pt_clone);
                self.add_reference_points(uld_pts, &best_pt_clone);
            }
        }
    }

    pub fn place_leftover(
        &mut self,
        uld_pts: &mut HashMap<String, Vec<[i32; 4]>>,
        order: Vec<usize>,
    ) {
        let directs = DIRECTS;
        for &pid in &order {
            let pckg = &self.all_pkgs[pid];
            let mut poss_pts = Vec::new();
            let a = pckg.length;
            let b = pckg.width;
            let c = pckg.height;

            let orientations = vec![
                vec![a, b, c],
                vec![a, c, b],
                vec![b, a, c],
                vec![b, c, a],
                vec![c, a, b],
                vec![c, b, a],
            ];

            for (num, uid) in self.all_ulds.iter().enumerate() {
                for ref_pt in &uld_pts[&uid.id] {
                    let [mut xx, mut yy, mut zz, dir_idx] = *ref_pt;

                    for args in &orientations {
                        xx = ref_pt[0] + args[0] as i32 * directs[dir_idx as usize][0];
                        yy = ref_pt[1] + args[1] as i32 * directs[dir_idx as usize][1];
                        zz = ref_pt[2] + args[2] as i32 * directs[dir_idx as usize][2];
                        if xx < 0 || yy < 0 || zz < 0 {
                            continue;
                        }
                        if self.final_checker(
                            num,
                            &[xx, yy, zz],
                            &[args[0] as i32, args[1] as i32, args[2] as i32],
                            pid,
                        ) {
                            poss_pts.push(vec![
                                pid,
                                self.all_ulds.iter().position(|u| u.id == uid.id).unwrap(),
                                xx.try_into().unwrap(),
                                yy.try_into().unwrap(),
                                zz.try_into().unwrap(),
                                args[0] as usize,
                                args[1] as usize,
                                args[2] as usize,
                                dir_idx.try_into().unwrap(),
                            ]);
                        }
                    }
                }
            }

            poss_pts.sort_by(|a, b| {
                let capacity_diff_a = self.all_ulds[a[1]].capacity() - self.uld_wts[a[1]] as f32;
                let capacity_diff_b = self.all_ulds[b[1]].capacity() - self.uld_wts[b[1]] as f32;
                capacity_diff_b
                    .partial_cmp(&capacity_diff_a)
                    .unwrap_or(Ordering::Equal)
                    .then_with(|| a[4].cmp(&b[4]))
                    .then_with(|| {
                        let abs_a = (a[2].min(
                            (self.all_ulds[a[1]].length as i32 - a[2] as i32 - a[5] as i32)
                                .try_into()
                                .unwrap(),
                        ) + a[3].min(
                            (self.all_ulds[a[1]].width as i32 - a[3] as i32 - a[6] as i32)
                                .try_into()
                                .unwrap(),
                        ));
                        let abs_b = (b[2].min(
                            (self.all_ulds[b[1]].length as i32 - b[2] as i32 - b[5] as i32)
                                .try_into()
                                .unwrap(),
                        ) + b[3].min(
                            (self.all_ulds[b[1]].width as i32 - b[3] as i32 - b[6] as i32)
                                .try_into()
                                .unwrap(),
                        ));
                        abs_a.partial_cmp(&abs_b).unwrap_or(Ordering::Equal)
                    })
                    .then_with(|| {
                        let dist_a = a[2] * a[2] + a[3] * a[3] + a[4] * a[4];
                        let dist_b = b[2] * b[2] + b[3] * b[3] + b[4] * b[4];
                        dist_a.cmp(&dist_b)
                    })
            });

            if poss_pts.is_empty() {
                continue;
            } else {
                let pt = &poss_pts[0];
                self.resultant_data.push((
                    pt[0],
                    pt[1],
                    pt[2] as i32,
                    pt[3] as i32,
                    pt[4] as i32,
                    (pt[2] + pt[5]) as i32,
                    (pt[3] + pt[6]) as i32,
                    (pt[4] + pt[7]) as i32,
                ));
                self.uld_wts[pt[1]] += pckg.weight as i32;

                let x_t = pt[2] - pt[5] * directs[pt[8]][0] as usize;
                let y_t = pt[3] - pt[6] * directs[pt[8]][1] as usize;
                let z_t = pt[4] - pt[7] * directs[pt[8]][2] as usize;

                if let Some(points) = uld_pts.get_mut(&self.all_ulds[pt[1]].id) {
                    points.retain(|x| *x != [x_t as i32, y_t as i32, z_t as i32, pt[8] as i32]);
                }
                self.add_point(
                    self.all_ulds[pt[1]].id.clone(),
                    x_t as i32,
                    y_t as i32,
                    z_t as i32,
                    pt[5] as i32,
                    pt[6] as i32,
                    pt[7] as i32,
                    uld_pts,
                );
            }
        }
    }

    pub fn check_new(
        &self,
        pid: usize,
        uid: usize,
        x: i32,
        y: i32,
        z: i32,
        x1: i32,
        y1: i32,
        z1: i32,
        new_res: &Vec<Vec<i32>>,
    ) -> bool {
        if x + x1 > self.all_ulds[uid].length as i32 {
            return false;
        }
        if y + y1 > self.all_ulds[uid].width as i32 {
            return false;
        }
        if z + z1 > self.all_ulds[uid].height as i32 {
            return false;
        }
        for ele in new_res {
            if ele[1] == uid as i32 {
                if check_intersection_cuboids(
                    [x, y, z],
                    [x + x1, y + y1, z + z1],
                    [ele[2], ele[3], ele[4]],
                    [ele[5], ele[6], ele[7]],
                ) {
                    return false;
                }
            }
        }
        true
    }

    pub fn push_to_side_face_first(&mut self, typ: i32) {
        let mut cpy_res = self.resultant_data.clone();
        let mut new_res = Vec::new();

        if typ == 1 {
            // Push to left face
            cpy_res.sort_by(|a, b| {
                let (_, _, a2, a3, a4, _, _, _) = a;
                let (_, _, b2, b3, b4, _, _, _) = b;
                a2.cmp(&b2).then(a3.cmp(&b3)).then(a4.cmp(&b4))
            });
            for ele in cpy_res {
                let (mut x_c, mut y_c, mut z_c, a, b, c) = (
                    ele.2,
                    ele.3,
                    ele.4,
                    ele.5 - ele.2,
                    ele.6 - ele.3,
                    ele.7 - ele.4,
                );
                let mut fct = false;
                while x_c > 0 {
                    x_c -= 1;
                    if !self.check_new(ele.0, ele.1, x_c, y_c, z_c, a, b, c, &new_res) {
                        new_res.push(vec![
                            ele.0 as i32,
                            ele.1 as i32,
                            x_c + 1,
                            y_c,
                            z_c,
                            x_c + a + 1,
                            y_c + b,
                            z_c + c,
                        ]);
                        fct = true;
                        break;
                    }
                }
                if !fct {
                    new_res.push(vec![
                        ele.0 as i32,
                        ele.1 as i32,
                        x_c,
                        y_c,
                        z_c,
                        x_c + a,
                        y_c + b,
                        z_c + c,
                    ]);
                }
            }
        }
        // Add logic for typ 2, 3, 4 similarly
        self.resultant_data = new_res
            .into_iter()
            .map(|v| {
                (
                    v[0] as usize,
                    v[1] as usize,
                    v[2],
                    v[3],
                    v[4],
                    v[5],
                    v[6],
                    v[7],
                )
            })
            .collect();
    }

    pub fn place_packages(&mut self) {
        let mut uld_pts = self.reset_uld_points();
        let mut uld_pts_map: HashMap<String, Vec<[i32; 4]>> = HashMap::new();
        for (i, uld) in self.all_ulds.iter().enumerate() {
            uld_pts_map.insert(
                uld.id.clone(),
                uld_pts[i]
                    .iter()
                    .map(|v| [v[0], v[1], v[2], v[3]])
                    .collect(),
            );
        }
        self.place_priority(&mut uld_pts_map);
        self.push_to_side_face_first(4);
        self.push_to_side_face_first(2);

        uld_pts = self.reset_uld_points();
        self.place_economy(&mut uld_pts_map);
        self.push_to_side_face_first(4);
        self.push_to_side_face_first(2);

        uld_pts = self.reset_uld_points();
        let mut not_packed = Vec::new();
        for &val in &self.non_priority_order {
            let found = self.resultant_data.iter().any(|item| item.1 == val);
            if !found {
                not_packed.push(val);
            }
        }

        self.place_leftover(&mut uld_pts_map, not_packed);
    }

    pub fn find_fitness(&mut self) -> i32 {
        if !self.evaluated {
            let mut self_mut = self.clone();
            self_mut.evaluated = true;
            self_mut.decode();
            self_mut.place_packages();
            let mut cntns_priority = HashSet::new();

            for val in &self_mut.resultant_data {
                let (pkg_id, _, _, _, _, _, _, _) = val;
                if self_mut.all_pkgs[*pkg_id].priority == true {
                    self_mut.priority_packed += 1;
                    let (_, uid, _, _, _, _, _, _) = val;
                    cntns_priority.insert(*uid);
                }
            }

            self_mut.ulds_used_for_priority = cntns_priority.len();
            self_mut.fitness_score = 0;

            for val in &self_mut.resultant_data {
                let (pkg_id, _, _, _, _, _, _, _) = val;
                if self_mut.all_pkgs[*pkg_id].priority == true {
                    let (pkg_id, _, _, _, _, _, _, _) = val;
                    self_mut.fitness_score += self_mut.all_pkgs[*pkg_id].cost as i32;
                }
            }

            self_mut.tot = self_mut.all_pkgs.iter().map(|pkg| pkg.cost).sum();

            let score = self_mut.tot
                - self_mut.fitness_score as f32
                - PENALTY_COST as f32 * self_mut.priority_packed as f32
                + COST_PER_ULD as f32 * self_mut.ulds_used_for_priority as f32;

            self_mut.fitness_score = score as i32;
            return self_mut.fitness_score;
        }
        let mut self_mut = self.clone();
        self_mut.evaluated = true;
        self_mut.decode();
        self_mut.place_packages();
        self_mut.priority_packed = 0;
        let mut cntns_priority = HashSet::new();

        for val in &self_mut.resultant_data {
            let (pkg_id, _, _, _, _, _, _, _) = val;
            if self.all_pkgs[*pkg_id].priority == true {
                self.priority_packed += 1;
                let (_, uid, _, _, _, _, _, _) = val;
                cntns_priority.insert(*uid);
            }
        }

        self.ulds_used_for_priority = cntns_priority.len();
        self.fitness_score = 0;

        for val in &self.resultant_data {
            let (pkg_id, _, _, _, _, _, _, _) = val;
            if !self.all_pkgs[*pkg_id].priority {
                self.fitness_score += self.all_pkgs[*pkg_id].cost as i32;
            }
        }

        self.tot = self.all_pkgs.iter().map(|pkg| pkg.cost).sum();

        let score = self.tot
            - self.fitness_score as f32
            - PENALTY_COST as f32 * self.priority_packed as f32
            + COST_PER_ULD as f32 * self.ulds_used_for_priority as f32;

        self.fitness_score = score as i32;
        self.fitness_score
    }

    pub fn store(&mut self, file_name: &str) {
        if !self.evaluated {
            self.fitness_score = self.find_fitness();
        }

        let data = format!("{:?}_{}", self.resultant_data, self.fitness_score);
        let mut file = File::create(file_name).expect("Failed to create file");
        file.write_all(data.as_bytes())
            .expect("Failed to write data to file");
    }
}

#[derive(Clone)]
pub struct GeneticSolver {
    org_pkgs: Vec<Package>,
    org_ulds: Vec<ULD>,
    uld_cnt: usize,
    pkg_cnt: usize,
    pop_size: usize,
    cnt_genes: usize,
    elites: usize,
    elite_crossover_prob: f64,
}

impl GeneticSolver {
    pub fn new(
        pkgs: Vec<Package>,
        ulds: Vec<ULD>,
        pop_size: usize,
        cnt_genes: usize,
        elites: usize,
        elite_crossover_prob: f64,
    ) -> Self {
        let uld_cnt = ulds.len();
        let pkg_cnt = pkgs.len();
        GeneticSolver {
            org_pkgs: pkgs,
            org_ulds: ulds,
            uld_cnt,
            pkg_cnt,
            pop_size,
            cnt_genes,
            elites,
            elite_crossover_prob,
        }
    }

    pub fn crossover(&self, elite: &Config, non_elite: &Config) -> Config {
        let mut offspring = Config::new(self.org_pkgs.clone(), self.org_ulds.clone());
        offspring.initialize();

        for i in 0..self.uld_cnt {
            if rand::thread_rng().gen::<f64>() < self.elite_crossover_prob {
                offspring.enc_priority_ord[i] = elite.enc_priority_ord[i];
            } else {
                offspring.enc_priority_ord[i] = non_elite.enc_priority_ord[i];
            }
        }

        for i in 0..self.pkg_cnt {
            if rand::thread_rng().gen::<f64>() < self.elite_crossover_prob {
                offspring.enc_non_priority_ord[i] = elite.enc_non_priority_ord[i];
            } else {
                offspring.enc_non_priority_ord[i] = non_elite.enc_non_priority_ord[i];
            }
        }

        offspring
    }

    pub fn run(&mut self) -> Solution {
        let mut population: Vec<Config> = Vec::with_capacity(self.pop_size);

        // Initialize population
        for _ in 0..self.pop_size {
            let mut cnfg = Config::new(self.org_pkgs.clone(), self.org_ulds.clone());
            cnfg.initialize();
            population.push(cnfg);
        }

        // Sort by fitness (ascending)
        population.sort_by(|a, b| {
            a.clone()
                .find_fitness()
                .partial_cmp(&b.clone().find_fitness())
                .unwrap_or(Ordering::Equal)
        });

        // Run through generations
        for gen in 0..self.cnt_genes {
            let mut new_pop: Vec<Config> = population.iter().take(self.elites).cloned().collect();

            let elite_pop = &population[0..self.elites];
            let non_elite_pop = &population[self.elites..];

            let rand_elite = elite_pop[rand::thread_rng().gen_range(0..self.elites)].clone();
            let rand_non_elite =
                non_elite_pop[rand::thread_rng().gen_range(0..non_elite_pop.len())].clone();

            let offspring = self.crossover(&rand_elite, &rand_non_elite);
            new_pop.push(offspring);

            // Perform mutation
            for _ in 0..self.pop_size - 1 - self.elites {
                let mut rand_cnfg = Config::new(self.org_pkgs.clone(), self.org_ulds.clone());
                rand_cnfg.initialize();
                new_pop.push(rand_cnfg);
            }

            population = new_pop;
            population.sort_by(|a, b| {
                a.clone()
                    .find_fitness()
                    .partial_cmp(&b.clone().find_fitness())
                    .unwrap_or(Ordering::Equal)
            });

            // Store best result every 5 generations after the first 5 generations
            let filename = gen.to_string();
            if gen >= 5 && gen % 5 == 0 {
                population[0].store(&filename);
            }
        }

        // Return the resultant data from the best configuration
        let best_config = &population[0];
        Solution {
            uld_order: best_config.priority_order.clone(),
            pack_order: best_config.non_priority_order.clone(),
            alloted: best_config.all_pkgs.clone(),
        }
    }
}
