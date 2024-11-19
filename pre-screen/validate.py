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
    def __init__(self, x1, y1, z1, x2, y2, z2):
        super().__init__(x1, y1, z1, x2, y2, z2)
        self.weight = None
        self.id = None
        self.score = None

    def __repr__(self):
        return f"Package({self.x1}, {self.y1}, {self.z1}, {self.x2}, {self.y2}, {self.z2}, {self.weight})"

    # Validates that the package is a valid rotation of the package in the package_data
    # and sets the weight and score of the package
    # Throws a ValueError if the package is not valid
    def validate_against_package(self, package_data: pd.DataFrame, package_id: int):
        package = package_data.loc[package_id == package_data["id"]].iloc[0]

        self.weight = package["weight"]
        self.score = package["score"]
        self.id = package_id

        l = package["length"]
        w = package["width"]
        h = package["height"]

        rotated = False
        # Check if the current is a rotated version of the package
        for perm in permutations([l, w, h]):
            if (
                self.length == perm[0]
                and self.width == perm[1]
                and self.height == perm[2]
            ):
                rotated = True
                break

        if not rotated:
            raise ValueError(
                f"Package {package_id} is not a valid rotation of the package"
            )


class ULD(Cuboid):
    def __init__(self, id, l, w, h, cap):
        super().__init__(0, 0, 0, l, w, h)
        self.id = id
        self.capacity = cap
        self.containing_packages = []
        self.score = 0

    def __repr__(self):
        return f"ULD({self.id}, {self.length}, {self.width}, {self.height}, {self.capacity}), {self.containing_packages})"

    def add_package(self, package: Package):
        self.containing_packages.append(package)
        self.score += package.score

    # Validates that the ULD is valid
    # Throws a ValueError if the ULD is invalid
    def validate(self):
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

        # Spatial Validation
        for package in self.containing_packages:
            # Check if the package is on top of another package or on the ground
            is_on_top = False
            for other_package in self.containing_packages:
                if package.id != other_package.id and package.on_top_of(other_package):
                    is_on_top = True
                    break
            if not is_on_top and package.z1 != 0:
                raise ValueError(
                    f"Package {package.id} is not on top of any package or on ground"
                )

        # Boundary Validation
        for package in self.containing_packages:
            if not package.contained_in(self):
                raise ValueError(
                    f"Package {package.id} is not contained in ULD {self.id}"
                )


# Validates the solution given the ULD, packages, and solution CSV files
def validate_solution(uld_path: str, packages_path: str, solution_path: str):
    uld_df = pd.read_csv(uld_path)

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

    package_data = pd.read_csv(packages_path)

    seen_packages = set()
    with open(solution_path) as file:
        data_lines = file.readlines()
        expected_score = int(data_lines[0].strip())
        number_packages = int(data_lines[1].strip())

        solution_data = pd.read_csv(
            solution_path,
            skiprows=2,
            names=["package_id", "uld_id", "x1", "y1", "z1", "x2", "y2", "z2"],
        )

        # If any ULD ID or package ID is None, remove the row
        # and log a warning
        if solution_data.isnull().values.any():
            print("Warning: Some ULD ID or package ID is None")
            solution_data = solution_data.dropna(subset=["package_id", "uld_id"])

        assert solution_data.shape[0] == number_packages, (
            f"Number of packages in solution does not match expected number, "
            f"got {solution_data.shape[0]} and {number_packages}"
        )

        for row in solution_data.iterrows():
            row = row[1]
            uld_id = row["uld_id"]
            assert uld_id in uld_ids, f"ULD {uld_id} is not a valid ULD ID"

            package_id = row["package_id"]
            assert (
                package_id in package_data["id"]
            ), f"Package {package_id} is not a valid package ID"

            package = Package(
                row["x1"], row["y1"], row["z1"], row["x2"], row["y2"], row["z2"]
            )
            package.validate_against_package(package_data, package_id)

            if package_id in seen_packages:
                raise ValueError(f"Package {package_id} is placed multiple times")
            seen_packages.add(package_id)

            for uld in ulds:
                if uld.id == uld_id:
                    uld.add_package(package)
                    break

    total_score = 0
    for uld in ulds:
        try:
            uld.validate()
            total_score += uld.score
        except ValueError as e:
            print(f"ULD {uld.id} is invalid: {e}")

    assert (
        total_score == expected_score
    ), f"Total score does not match expected score, got {total_score} and {expected_score}"

    print(f"OK: Score = {total_score}, Package Count = {number_packages}")


if __name__ == "__main__":
    validate_solution(
        "./uld.csv",
        "./packages.csv",
        "./solution.csv",
    )
