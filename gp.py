import csv

from utils import load_dfs, generate_solution_file
from validator import validate_solution


class Package:
    def __init__(
        self, identifier, length, width, height, weight, package_type, cost_of_delay
    ):
        self.identifier = identifier
        self.length = length
        self.width = width
        self.height = height
        self.weight = weight
        self.package_type = package_type
        self.cost_of_delay = cost_of_delay
        self.coordinates = None


class ULD:
    def __init__(self, identifier, length, width, height, weight_limit):
        self.identifier = identifier
        self.length = length
        self.width = width
        self.height = height
        self.weight_limit = weight_limit
        self.remaining_weight = weight_limit
        self.remaining_space = [(0, 0, 0, length, width, height)]
        self.packages = []

    def can_fit_package(self, package):
        if package.weight > self.remaining_weight:
            return False
        for _, _, _, l, w, h in self.remaining_space:
            if package.length <= l and package.width <= w and package.height <= h:
                return True

        return False

    def place_package(self, package):
        for index, (x, y, z, l, w, h) in enumerate(self.remaining_space):
            if package.length <= l and package.width <= w and package.height <= h:
                self.packages.append(package)
                self.remaining_weight -= package.weight

                package.coordinates = (x, y, z)

                self.remaining_space.pop(index)
                self.remaining_space.append(
                    (x + package.length, y, z, l - package.length, w, h)
                )  # Right split
                self.remaining_space.append(
                    (x, y + package.width, z, l, w - package.width, h)
                )  # Front split
                self.remaining_space.append(
                    (x, y, z + package.height, l, w, h - package.height)
                )  # Top split
                return True

        return False


def guillotine_packing(ulds, packages):
    for package in packages:
        for uld in ulds:
            if uld.can_fit_package(package):
                uld.place_package(package)
                break

    return ulds


def run():
    package_data, uld_data = load_dfs()

    ulds = [
        ULD(
            row["id"],
            row["length"],
            row["width"],
            row["height"],
            row["capacity"],
        )
        for _, row in uld_data.iterrows()
    ]

    packages = [
        Package(
            row["id"],
            row["length"],
            row["width"],
            row["height"],
            row["weight"],
            row["priority"],
            row["cost"],
        )
        for _, row in package_data.iterrows()
    ]

    packages.sort(key=lambda x: (x.cost_of_delay, x.package_type), reverse=True)
    packed_ulds = guillotine_packing(ulds, packages)

    with open("./data/gp_raw.csv", "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["uld_idx", "package_idx", "x", "y", "z"])
        for uld in packed_ulds:
            for package in uld.packages:
                writer.writerow(
                    [
                        int(uld.identifier[1]) - 1,
                        int(package.identifier[2:]) - 1,
                        *package.coordinates,
                    ]
                )

    generate_solution_file("./data/gp_raw.csv", "./data/gp_solution.csv")
    validate_solution("./data/gp_solution.csv")


if __name__ == "__main__":
    run()
