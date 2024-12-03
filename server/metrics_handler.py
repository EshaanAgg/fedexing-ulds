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
