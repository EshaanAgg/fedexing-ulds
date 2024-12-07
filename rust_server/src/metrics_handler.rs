#![allow(warnings, unused)]

use serde::Deserialize;

#[derive(Debug, Clone)]
pub struct Vector {
    x: f64,
    y: f64,
    z: f64,
}

impl Vector {
    pub fn new(x: f64, y: f64, z: f64) -> Self {
        Self { x, y, z }
    }

    pub fn add(&self, other: &Vector) -> Vector {
        Vector::new(self.x + other.x, self.y + other.y, self.z + other.z)
    }

    pub fn scale(&self, scalar: f64) -> Vector {
        Vector::new(self.x * scalar, self.y * scalar, self.z * scalar)
    }

    pub fn mult(&self, other: &Vector) -> Vector {
        Vector::new(self.x * other.x, self.y * other.y, self.z * other.z)
    }

    pub fn distance_z(&self, other: &Vector) -> f64 {
        (self.x - other.x).powi(2) + (self.y - other.y).powi(2)
    }

    pub fn distance_2d(&self, x: f64, y: f64) -> f64 {
        (self.x - x).powi(2) + (self.y - y).powi(2)
    }
}

#[derive(Debug, Clone, Deserialize)]
pub struct RequestItem {
    x1: f64,
    y1: f64,
    z1: f64,
    x2: f64,
    y2: f64,
    z2: f64,
    weight: f64,
}

impl RequestItem {
    pub fn length(&self) -> f64 {
        self.x2 - self.x1
    }

    pub fn width(&self) -> f64 {
        self.y2 - self.y1
    }

    pub fn height(&self) -> f64 {
        self.z2 - self.z1
    }

    pub fn center(&self) -> Vector {
        Vector::new(
            (self.x2 + self.x1) / 2.0,
            (self.y2 + self.y1) / 2.0,
            (self.z2 + self.z1) / 2.0,
        )
    }

    pub fn volume(&self) -> f64 {
        self.length() * self.width() * self.height()
    }
}

#[derive(Debug, Deserialize)]
pub struct Request {
    uld_length: f64,
    uld_width: f64,
    uld_height: f64,
    uld_weight: f64,
    pub packages: Vec<RequestItem>,
}

pub fn get_volumetric_center(pkgs: &[RequestItem]) -> Vector {
    let mut v = 0.0;
    let mut v_center = Vector::new(0.0, 0.0, 0.0);

    for pkg in pkgs {
        v += pkg.volume();
        v_center = v_center.add(&pkg.center().scale(pkg.volume()));
    }

    if v == 0.0 {
        return v_center;
    }

    v_center.scale(1.0 / v)
}

pub fn moi_metric(req: &Request) -> f64 {
    let pkgs = &req.packages;
    let v_center = get_volumetric_center(pkgs);

    let mut moi_min = 0.0;
    let mut moi_corners = vec![0.0; 4];
    let corners = vec![
        (0.0, 0.0),
        (req.uld_length, 0.0),
        (0.0, req.uld_width),
        (req.uld_length, req.uld_width),
    ];

    for pkg in pkgs {
        moi_min += pkg.weight * pkg.center().distance_z(&v_center);
        for (i, corner) in corners.iter().enumerate() {
            moi_corners[i] += pkg.weight * pkg.center().distance_2d(corner.0, corner.1);
        }
    }

    if moi_min == 0.0 {
        return 0.0;
    }

    (moi_corners.iter().copied().sum::<f64>() / 4.0 + moi_corners.iter().copied().map(|x| (x - moi_corners.iter().copied().sum::<f64>() / 4.0).powi(2)).sum::<f64>().sqrt()) / moi_min
}

pub fn used_space(req: &Request) -> f64 {
    if req.uld_height == 0.0 || req.uld_width == 0.0 || req.uld_length == 0.0 {
        return 0.0;
    }

    req.packages.iter().map(|pkg| pkg.volume()).sum::<f64>()
        / (req.uld_length * req.uld_width * req.uld_height)
}

pub fn used_weight(req: &Request) -> f64 {
    if req.uld_weight == 0.0 {
        return 0.0;
    }

    req.packages.iter().map(|pkg| pkg.weight).sum::<f64>() / req.uld_weight
}

pub fn stability(req: &Request) -> f64 {
    if req.packages.is_empty() {
        return 0.0;
    }

    let mut base_support_area = 0.0;
    let mut center_of_gravity_height = 0.0;
    let mut stacking_stability = 0.0;
    let mut weighted_x_sum = 0.0;
    let mut weighted_y_sum = 0.0;

    let total_weight: f64 = req.packages.iter().map(|pkg| pkg.weight).sum();

    for pkg in &req.packages {
        let mx_base_area = f64::max(
            pkg.length() * pkg.width(),
            f64::max(pkg.length() * pkg.height(), pkg.width() * pkg.height()),
        );
        base_support_area += pkg.length() * pkg.width() / mx_base_area;

        center_of_gravity_height += ((pkg.z1 + pkg.z2) / 2.0 / req.uld_height) * (pkg.weight / total_weight);

        weighted_x_sum += pkg.center().x * pkg.weight;
        weighted_y_sum += pkg.center().y * pkg.weight;
    }

    for pkg in &req.packages {
        let below_packages: Vec<_> = req.packages.iter().filter(|other| {
            other.x1 < pkg.x2 && other.x2 > pkg.x1 && other.y1 < pkg.y2 && other.y2 > pkg.y1 && other.z2 <= pkg.z1
        }).collect();

        let stacked_weight: f64 = below_packages.iter().map(|other| other.weight).sum();
        stacking_stability += if stacked_weight >= pkg.weight { 1.0 } else { 0.0 };
    }

    base_support_area /= req.packages.len() as f64;
    stacking_stability /= req.packages.len() as f64;

    let center_x = weighted_x_sum / total_weight;
    let center_y = weighted_y_sum / total_weight;
    let deviation_from_center = ((center_x - req.uld_length / 2.0).powi(2) + (center_y - req.uld_width / 2.0).powi(2)).sqrt();
    let placement_distribution = 1.0 - (deviation_from_center / ((req.uld_length + req.uld_width) / 4.0));

    0.2 * base_support_area
        + 0.2 * (1.0 - center_of_gravity_height)
        + 0.5 * placement_distribution
        + 0.1 * stacking_stability
        + 0.08
}
