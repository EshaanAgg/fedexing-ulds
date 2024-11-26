import time
import random
import pandas as pd
from packer import Packer

random.seed(time.time())


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


def run():
    ensure_dataset()
    packer = Packer(
        "./data/packages.csv",
        "./data/ulds.csv",
        cpu_limit=50,
    )

    solution = packer.best_solution
    pd.DataFrame(solution).to_csv("./data/solution.csv", index=False)
    print(packer.best_metrics)


if __name__ == "__main__":
    run()
