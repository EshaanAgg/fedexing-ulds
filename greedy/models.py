import pandas as pd
from enum import Enum
from typing import List


class Package:
    def __init__(
        self,
        id: str,
        x: int,
        y: int,
        z: int,
        w: int,
        cost: int = 0,
        priority_item: bool = False,
        fragile_item: bool = False,
        heavy_item: bool = False,
        placed_on: List[bool] = [True, True, True],
    ):
        """
        Define a package object with the respective attributes.

        x, y, z represents the length, width, and height of the package.
        "heavy" items are only to be placed on the floor of the ULD.
        "fragile" items cannot be stacked upon.
        placed_on is a list of 3 booleans that represent if the package can be placed on the XZ surface, XY surface, and YZ surface respectively.
        """
        self.id = id
        self.x = x
        self.y = y
        self.z = z
        self.weight = w
        self.cost = cost
        self.priority = priority_item
        self.fragile = fragile_item
        self.heavy = heavy_item
        self.placed_on = placed_on

        if not any(placed_on):
            raise ValueError("Package cannot be placed on any surface.")
        if fragile_item and heavy_item:
            raise ValueError("An item cannot be both fragile and heavy.")

        # Possible orientations of the package
        self.orients = []
        if placed_on[0]:
            self.orients.append("xzy")
            self.orients.append("zxy")
        if placed_on[1]:
            self.orients.append("xyz")
            self.orients.append("yxz")
        if placed_on[2]:
            self.orients.append("yzx")
            self.orients.append("zyx")

        # Sort the orientations based on the base area
        self.orients.sort(
            key=lambda x: self.get_dim(x[0]) * self.get_dim(x[1]),
            reverse=True,
        )

        self.volume = x * y * z
        self.mx_dim = max(x, y, z)

        self.assigned_uld = None
        self.pt1 = (None, None, None)
        self.pt2 = (None, None, None)

    def reset(self):
        """
        Reset the package attributes.
        """
        self.assigned_uld = None
        self.pt1 = (None, None, None)
        self.pt2 = (None, None, None)

    def place_in_uld(self, uld_idx, ref_pt, opp_pt):
        """
        Place the package in the ULD.
        """
        self.assigned_uld = uld_idx
        self.pt1 = ref_pt
        self.pt2 = opp_pt

    def get_dim(self, ch) -> int:
        """
        Returns the dimension of the package.
        """
        if ch == "x":
            return self.x
        if ch == "y":
            return self.y
        if ch == "z":
            return self.z
        raise ValueError("Invalid dimension.")

    def __str__(self):
        return f"Package {self.id} ({self.x}, {self.y}, {self.z})"

    def __repr__(self):
        return f"Package {self.id} ({self.x}, {self.y}, {self.z})"

    def load_from_df(file: str) -> List["Package"]:
        """
        Load packages from a CSV file.
        """
        df = pd.read_csv(file)
        packages = []

        for _, row in df.iterrows():
            packages.append(
                Package(
                    row["id"],
                    row["x"],
                    row["y"],
                    row["z"],
                    row["weight"],
                    row["cost"],
                    row["priority"],
                    row["fragile"],
                    row["heavy"],
                    placed_on=[
                        row["placed_on_xz"],
                        row["placed_on_xy"],
                        row["placed_on_yz"],
                    ],
                )
            )

        return packages

    def contains(self, x, y, z):
        """
        Checks if the point (x, y, z) is inside the package.
        This method must be called after the package is placed in the ULD.
        """

        if self.assigned_uld is None:
            raise ValueError("Package is not placed in any ULD.")

        x1, y1, z1 = self.pt1
        x2, y2, z2 = self.pt2
        if x > x1 and x < x2 and y > y1 and y < y2 and z > z1 and z < z2:
            return True

        return False

    def get_intersection_volume(self, x1, y1, z1, x2, y2, z2):
        """
        This method calculates the intersection volume of the package with the
        cuboid defined by the points (x1, y1, z1) and (x2, y2, z2).
        This method must be called after the package is placed in the ULD.
        """

        if self.assigned_uld is None:
            raise ValueError("Package is not placed in any ULD.")

        dx = min(x2, self.pt2[0]) - max(x1, self.pt1[0])
        dy = min(y2, self.pt2[1]) - max(y1, self.pt1[1])
        dz = min(z2, self.pt2[2]) - max(z1, self.pt1[2])

        if dx < 0 or dy < 0 or dz < 0:
            return 0

        return dx * dy * dz


class ULD:
    def __init__(self, id: str, x: int, y: int, z: int, w: int):
        """
        Define a ULD object with the respective attributes.
        """
        self.id = id
        self.x = x
        self.y = y
        self.z = z
        self.weight = w

        self.volume = x * y * z

        self.packed_volume = 0  # Volume of the packages packed in the ULD
        self.packed_weight = 0  # Weight of the packages packed in the ULD
        self.package_idx = []  # Index of the packages packed in the ULD
        self.has_priority = False  # If the ULD has a priority package

        # Reference points for the ULD
        self.ref_pts = [(0, 0, 0)]

    def __str__(self):
        return f"ULD {self.id} ({self.x}, {self.y}, {self.z})"

    def __repr__(self):
        return f"ULD {self.id} ({self.x}, {self.y}, {self.z})"

    def load_from_df(file: str) -> List["ULD"]:
        """
        Load ULDs from a CSV file.
        """
        df = pd.read_csv(file)
        ulds = []

        for _, row in df.iterrows():
            ulds.append(ULD(row["id"], row["x"], row["y"], row["z"], row["weight"]))

        return ulds

    def out_of_bounds(self, x, y, z):
        """
        Check if the provided point is out of bounds of the ULD.
        """
        return x < 0 or y < 0 or z < 0 or x > self.x or y > self.y or z > self.z

    def add_package(self, pack: Package, pack_idx: int, ref_pt, opp_pt):
        """
        Add a package to the ULD.
        """

        self.ref_pts.remove(ref_pt)

        # If not fragile, add to the reference points
        if not pack.fragile:
            opp_x, opp_y, opp_z = opp_pt
            origin_x, origin_y, origin_z = ref_pt
            self.ref_pts.append((opp_x, origin_y, origin_z))
            self.ref_pts.append((origin_x, opp_y, origin_z))
            self.ref_pts.append((origin_x, origin_y, opp_z))

        # Update the ULD attributes
        self.package_idx.append(pack_idx)
        self.packed_volume += pack.volume
        self.packed_weight += pack.weight
        self.has_priority = self.has_priority or pack.priority

    def reset(self):
        """
        Reset the ULD attributes.
        """
        self.packed_volume = 0
        self.packed_weight = 0
        self.package_idx = []
        self.has_priority = False
        self.ref_pts = [(0, 0, 0)]


class FFDecr(Enum):
    """
    Define the first fit decreasing algorithms.
    """

    WEIGHT = "weight"
    VOLUME = "volume"
    MAX_DIM = "max_dim"

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value


class ConstructiveHeuristic(Enum):
    """
    Define the constructive heuristics.
    """

    LAYER = "layer"
    COLUMN = "column"
    WALL = "wall"

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value
