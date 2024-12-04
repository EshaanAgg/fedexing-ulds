import numpy as np
from pydantic import BaseModel, computed_field


class Vector:
    def __init__(self, x, y, z) -> None:
        self.x = x
        self.y = y
        self.z = z

    def add(self, other: "Vector") -> "Vector":
        return Vector(self.x + other.x, self.y + other.y, self.z + other.z)

    def scale(self, scalar: float) -> "Vector":
        return Vector(self.x * scalar, self.y * scalar, self.z * scalar)

    def mult(self, other: "Vector") -> "Vector":
        return Vector(self.x * other.x, self.y * other.y, self.z * other.z)

    def distanceZ(self, other: "Vector") -> float:
        return (self.x - other.x) ** 2 + (self.y - other.y) ** 2

    def distance_2d(self, x: float, y: float) -> float:
        return (self.x - x) ** 2 + (self.y - y) ** 2


class RequestItem(BaseModel):
    x1: float
    y1: float
    z1: float
    x2: float
    y2: float
    z2: float
    weight: float

    @computed_field
    def length(self) -> float:
        return self.x2 - self.x1

    @computed_field
    def width(self) -> float:
        return self.y2 - self.y1

    @computed_field
    def height(self) -> float:
        return self.z2 - self.z1

    @computed_field
    def center(self) -> Vector:
        return Vector(
            (self.x2 + self.x1) / 2,
            (self.y2 + self.y1) / 2,
            (self.z2 + self.z1) / 2,
        )

    @computed_field
    def volume(self) -> float:
        return self.length * self.width * self.height

    class Config:
        arbitrary_types_allowed = True


class Request(BaseModel):
    uld_length: float
    uld_width: float
    uld_height: float
    uld_weight: float
    packages: list[RequestItem]


def get_volumetric_center(pkgs: list[RequestItem]) -> Vector:
    V = 0
    V_center = Vector(0, 0, 0)

    for pkg in pkgs:
        V += pkg.volume
        V_center = V_center.add(pkg.center.scale(pkg.volume))

    if V == 0:
        return V_center
    return V_center.scale(1 / V)


def moi_metric(req: Request) -> float:
    pkgs = req.packages
    V_center = get_volumetric_center(pkgs)
    MOI_MIN = 0

    MOI_CORNERS = [0 for _ in range(4)]
    corners = [
        (0, 0),
        (req.uld_length, 0),
        (0, req.uld_width),
        (req.uld_length, req.uld_width),
    ]

    for pkg in pkgs:
        MOI_MIN += pkg.weight * pkg.center.distanceZ(V_center)
        for i, corner in enumerate(corners):
            MOI_CORNERS[i] += pkg.weight * pkg.center.distance_2d(*corner)

    if MOI_MIN == 0:
        return 0
    return (np.mean(MOI_CORNERS) + np.std(MOI_CORNERS)) / MOI_MIN


def used_space(req: Request) -> float:
    if req.uld_height == 0 or req.uld_width == 0 or req.uld_length == 0:
        return 0

    return sum(pkg.volume for pkg in req.packages) / (
        req.uld_length * req.uld_width * req.uld_height
    )


def used_weight(req: Request) -> float:
    if req.uld_weight == 0:
        return 0
    return sum(pkg.weight for pkg in req.packages) / req.uld_weight


def stability(req: Request):
    if len(req.packages) == 0:
        return 0

    base_support_area = 0
    center_of_gravity_height = 0
    stacking_stability = 0
    weighted_x_sum = 0
    weighted_y_sum = 0

    total_weight = sum(pkg.weight for pkg in req.packages)

    for pkg in req.packages:
        mx_base_area = max(
            pkg.length * pkg.width,
            pkg.length * pkg.height,
            pkg.width * pkg.height,
        )
        base_support_area += pkg.length * pkg.width / mx_base_area

        center_of_gravity_height += (
            (pkg.z1 + pkg.z2) / 2 / req.uld_height * (pkg.weight / total_weight)
        )

        weighted_x_sum += pkg.center.x * pkg.weight
        weighted_y_sum += pkg.center.y * pkg.weight

    # Stacking stability: penalize heavier packages on lighter ones
    for pkg in req.packages:
        below_packages = [
            other
            for other in req.packages
            if (
                other.x1 < pkg.x2
                and other.x2 > pkg.x1
                and other.y1 < pkg.y2
                and other.y2 > pkg.y1
                and other.z2 <= pkg.z1
            )
        ]
        stacked_weight = sum(other.weight for other in below_packages)
        stacking_stability += 1 if stacked_weight >= pkg.weight else 0

    base_support_area /= len(req.packages)
    stacking_stability /= len(req.packages)

    center_x = weighted_x_sum / total_weight
    center_y = weighted_y_sum / total_weight
    deviation_from_center = (
        (center_x - req.uld_length / 2) ** 2 + (center_y - req.uld_width / 2) ** 2
    ) ** 0.5
    placement_distribution = 1 - (
        deviation_from_center / ((req.uld_length + req.uld_width) / 4)
    )

    return (
        0.2 * base_support_area
        + 0.2 * (1 - center_of_gravity_height)
        + 0.5 * placement_distribution
        + 0.1 * stacking_stability
    ) + 0.08
