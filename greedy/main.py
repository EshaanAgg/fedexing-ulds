import time
import random
import pandas as pd
from collections import defaultdict

from packer import Packer

random.seed(time.time())


class Cuboid:
    def __init__(self, x1, y1, z1, x2, y2, z2):
        self.x1, self.y1, self.z1 = x1, y1, z1
        self.x2, self.y2, self.z2 = x2, y2, z2

    def get_intersection_volume(self, other: "Cuboid"):
        dx = min(self.x2, other.x2) - max(self.x1, other.x1)
        dy = min(self.y2, other.y2) - max(self.y1, other.y1)
        dz = min(self.z2, other.z2) - max(self.z1, other.z1)
        if dx < 0 or dy < 0 or dz < 0:
            return 0
        return dx * dy * dz


def ensure_dataset():
    """
    Ensure the dataset is available.
    """
    try:
        pd.read_csv("./data/packages.csv")
    except FileNotFoundError:
        packages = pd.read_csv(
            "./packages_raw.csv",
            header=0,
            names=["id", "x", "y", "z", "weight", "priority", "cost"],
        )

        packages["priority"] = packages["priority"].apply(lambda x: x == "Priority")
        packages["cost"] = packages["cost"].apply(lambda x: 0 if x == "-" else int(x))

        for col, default in (
            ("fragile", False),
            ("heavy", False),
            ("placed_on_xz", True),
            ("placed_on_xy", True),
            ("placed_on_yz", True),
        ):
            packages[col] = default

        packages.to_csv("./data/packages.csv", index=False)

        # Process the ULDs dataset
        ulds = pd.read_csv(
            "./ulds_raw.csv",
            header=0,
            names=["id", "x", "y", "z", "weight"],
        )
        ulds.to_csv("./data/ulds.csv", index=False)


def check_intersectios(solution):
    packages = defaultdict(list)
    for row in solution:
        packages[row["uld_id"]].append(
            Cuboid(
                row["x1"],
                row["y1"],
                row["z1"],
                row["x2"],
                row["y2"],
                row["z2"],
            )
        )

    for uld_id, cuboids in packages.items():
        for i, cuboid in enumerate(cuboids):
            for other in cuboids[i + 1 :]:
                assert (
                    cuboid.get_intersection_volume(other) == 0
                ), f"Intersecting cuboids in ULD {uld_id}"


def run():
    ensure_dataset()
    packer = Packer(
        "./data/packages.csv",
        "./data/ulds.csv",
        cpu_limit=50,
    )

    solution = packer.best_solution
    check_intersectios(solution)

    pd.DataFrame(solution).to_csv("./data/solution.csv", index=False)
    print(packer.best_metrics)


if __name__ == "__main__":
    run()
