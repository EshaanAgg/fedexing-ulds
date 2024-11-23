import sys
import pandas as pd
from typing import Optional
from itertools import permutations


# Checks if the provided intervals [l1, r1] and [l2, r2] intersect
def interval_intersection(l1: int, r1: int, l2: int, r2: int) -> bool:
    return not (r1 <= l2 or r2 <= l1)


class Cuboid:
    # (x1, y1, z1) is the corner with smallest z, and then y, and then x
    # (x2, y2, z2) is the diagonally opposite corner
    def __init__(self, x1, y1, z1, x2, y2, z2):
        assert x1 < x2, f"x1 must be less than x2, got {x1} and {x2}"
        assert y1 < y2, f"y1 must be less than y2, got {y1} and {y2}"
        assert z1 < z2, f"z1 must be less than z2, got {z1} and {z2}"

        self.x1 = x1
        self.y1 = y1
        self.z1 = z1
        self.x2 = x2
        self.y2 = y2
        self.z2 = z2

        self.length = x2 - x1
        self.width = y2 - y1
        self.height = z2 - z1

    def volume(self) -> int:
        return self.length * self.width * self.height

    # Returns the intersection of two cuboids, or None if they don't intersect
    def intersection(self, other: "Cuboid") -> Optional["Cuboid"]:
        x1 = max(self.x1, other.x1)
        y1 = max(self.y1, other.y1)
        z1 = max(self.z1, other.z1)
        x2 = min(self.x2, other.x2)
        y2 = min(self.y2, other.y2)
        z2 = min(self.z2, other.z2)

        if x1 >= x2 or y1 >= y2 or z1 >= z2:
            return None

        return Cuboid(x1, y1, z1, x2, y2, z2)

    # Returns True if the two cuboids intersect
    def intersects(self, other: "Cuboid") -> bool:
        return self.intersection(other) is not None

    # Returns True if this cuboid is contained in the other cuboid
    def contained_in(self, other: "Cuboid") -> bool:
        return (
            self.x2 <= other.x2
            and self.y2 <= other.y2
            and self.z2 <= other.z2
            and self.x1 >= other.x1
            and self.y1 >= other.y1
            and self.z1 >= other.z1
        )

    # Checks if this cuboid is on top of other
    def on_top_of(self, other: "Cuboid") -> bool:
        return (
            self.z1 == other.z2
            and interval_intersection(self.x1, self.x2, other.x1, other.x2)
            and interval_intersection(self.y1, self.y2, other.y1, other.y2)
        )


class Package(Cuboid):
    def __init__(self, id, x1, y1, z1, x2, y2, z2, weight, is_priority, cost):
        super().__init__(x1, y1, z1, x2, y2, z2)
        self.id = id
        self.weight = weight
        self.is_priority = is_priority
        self.cost = cost

    def __repr__(self):
        return f"Package({self.x1}, {self.y1}, {self.z1}, {self.x2}, {self.y2}, {self.z2}, {self.weight})"

    def validate_against_dimensions(self, l, w, h):
        for dim in permutations([l, w, h]):
            if self.length == dim[0] and self.width == dim[1] and self.height == dim[2]:
                return

        raise ValueError(
            f"No rotation of package {self.id} does not match any of the provided dimensions"
        )


class ULD(Cuboid):
    def __init__(self, id, l, w, h, cap):
        super().__init__(0, 0, 0, l, w, h)
        self.id = id
        self.capacity = cap
        self.containing_packages = []
        self.has_priority = False

    def __repr__(self):
        return f"ULD({self.id}, {self.length}, {self.width}, {self.height}, {self.capacity}), {self.containing_packages})"

    def add_package(self, package: Package):
        self.containing_packages.append(package)
        if package.is_priority:
            self.has_priority = True

    # Validates that the ULD is valid
    # Throws a ValueError if the ULD is invalid
    def validate(self, use_spatial_validation=False):
        # Weight validation
        total_weight = sum(package.weight for package in self.containing_packages)
        if total_weight > self.capacity:
            raise ValueError(
                f"Total weight of packages in ULD {self.id} exceeds capacity"
            )

        # Intersection Validation
        for package in self.containing_packages:
            for other_package in self.containing_packages:
                if package.id != other_package.id and package.intersects(other_package):
                    raise ValueError(
                        f"Package {package.id} intersects with package {other_package.id}"
                    )

        # Boundary Validation
        for package in self.containing_packages:
            if not package.contained_in(self):
                raise ValueError(
                    f"Package {package.id} is not contained in ULD {self.id}"
                )

        # Spatial Validation
        if use_spatial_validation:
            for package in self.containing_packages:
                # Check if the package is on top of another package or on the ground
                is_on_top = False
                for other_package in self.containing_packages:
                    if package.id != other_package.id and package.on_top_of(
                        other_package
                    ):
                        is_on_top = True
                        break
                if not is_on_top and package.z1 != 0:
                    raise ValueError(
                        f"Package {package.id} is not on top of any package or on ground"
                    )


# Validates the solution given the ULD, packages, and solution CSV files
def validate_solution(
    solution_path: str,
    uld_path: str = "./data/ulds.csv",
    packages_path: str = "./data/packages.csv",
    use_spatial_validation=False,
    diff_package_cost: int = 5000,
):
    # Load the ULD data
    uld_df = pd.read_csv(
        uld_path,
        header=0,
        names=["id", "length", "width", "height", "limit"],
    )

    uld_ids = set()
    ulds = []
    for row in uld_df.iterrows():
        rv = row[1]
        uld = ULD(
            rv["id"],
            rv["length"],
            rv["width"],
            rv["height"],
            rv["limit"],
        )
        ulds.append(uld)
        uld_ids.add(uld.id)

    # Load the package data
    package_data = pd.read_csv(
        packages_path,
        header=0,
        names=["id", "length", "width", "height", "weight", "priority", "cost"],
    )
    package_data["priority"] = package_data["priority"].apply(
        lambda x: 1 if x == "Priority" else 0
    )
    package_data["cost"] = package_data["cost"].apply(
        lambda x: 0 if x == "-" else int(x)
    )

    # Validate the solution
    with open(solution_path) as file:
        data_lines = file.readlines()
        input_data = list(map(int, data_lines[0].strip().split()))

        assert len(input_data) == 3, "Expected 3 integers in the first line"
        expected_cost, number_packages, priority_ulds = input_data

    solution_data = pd.read_csv(
        solution_path,
        skiprows=1,
        names=["package_id", "uld_id", "x1", "y1", "z1", "x2", "y2", "z2"],
    )
    solution_data["uld_id"] = solution_data["uld_id"].apply(
        lambda x: x if x != "NONE" else None
    )

    # Check all packages are present in the solution EXACTLY once
    all_packages = set(package_data["id"])
    for pack in solution_data["package_id"]:
        assert pack in all_packages, f"Package {pack} not found in package data"
        all_packages.remove(pack)
    assert len(all_packages) == 0, f"Missing packages in solution"

    # Check that the non-null ULDs are valid
    count_packed = 0
    for row in solution_data.iterrows():
        uld = row[1]["uld_id"]
        if uld is not None:
            assert uld in uld_ids, f"ULD {uld} not found in ULD data"
            count_packed += 1
        else:
            # Check that all the coordinates are -1
            for coord in ["x1", "y1", "z1", "x2", "y2", "z2"]:
                assert (
                    row[1][coord] == -1
                ), f"Unpacked package {row[1]['package_id']} has non -1 coordinates"

    assert (
        count_packed == number_packages
    ), f"The number of packed packages does not match the reported number of packages"

    total_cost = 0
    for row in solution_data.iterrows():
        row = row[1]
        uld_id = row["uld_id"]

        package_id = row["package_id"]
        pack_item = package_data.loc[package_data["id"] == package_id].iloc[0]

        if row["uld_id"] is None:
            total_cost += pack_item["cost"]
            continue

        package = Package(
            package_id,
            row["x1"],
            row["y1"],
            row["z1"],
            row["x2"],
            row["y2"],
            row["z2"],
            pack_item["weight"],
            pack_item["priority"],
            pack_item["cost"],
        )
        package.validate_against_dimensions(
            pack_item["length"],
            pack_item["width"],
            pack_item["height"],
        )

        for uld in ulds:
            if uld.id == uld_id:
                uld.add_package(package)
                break

    for uld in ulds:
        try:
            uld.validate(use_spatial_validation)
        except ValueError as e:
            print(f"ULD {uld.id} is invalid: {e}")

    computed_priority_ulds = sum(uld.has_priority for uld in ulds)
    assert (
        computed_priority_ulds == priority_ulds
    ), f"Expected {priority_ulds} priority ULDs, got {computed_priority_ulds}"

    total_cost += priority_ulds * diff_package_cost
    assert (
        total_cost == expected_cost
    ), f"Expected cost {expected_cost}, got {total_cost}"

    print(
        f"OK: Cost = {total_cost}, Package Count = {number_packages}, Priority ULDs = {priority_ulds}"
    )


if __name__ == "__main__":
    outfile = sys.argv[1]
    validate_solution(outfile)
