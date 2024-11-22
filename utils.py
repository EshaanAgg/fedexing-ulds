import pandas as pd


def load_data(
    load_frac: float = 1.0,
    shuffle: bool = False,
    package_file: str = "./data/packages.csv",
    uld_file: str = "./data/ulds.csv",
):
    """
    Loads the ULD and package data from the CSV files and returns them as dictionaries.

    @param load_frac: The fraction of the package data to load (from the top). Default is 1.0.
    @param shuffle: Whether to shuffle the package data. Default is False.
    """

    data = {}

    uld_data = pd.read_csv(
        uld_file,
        header=0,
        names=["id", "length", "width", "height", "capacity"],
    )

    package_data = pd.read_csv(
        package_file,
        header=0,
        names=["id", "length", "width", "height", "weight", "priority", "cost"],
    )
    package_data["priority"] = package_data["priority"].apply(
        lambda x: True if x == "Priority" else False
    )
    package_data["cost"] = package_data["cost"].apply(
        lambda x: 1e9 if x == "-" else int(x)
    )

    if shuffle:
        package_data = package_data.sample(frac=1).reset_index(drop=True)
    package_data = package_data.iloc[: int(len(package_data) * load_frac)]

    data["ULDs"] = uld_data.to_dict(orient="records")
    data["packages"] = package_data.to_dict(orient="records")

    return data


def generate_solution_file(
    df,
    output_file: str = "./data/solution.csv",
    package_file: str = "./data/packages.csv",
    uld_file: str = "./data/ulds.csv",
    priority_spread_cost: int = 5000,
):
    """
    Generates a CSV file in the solution format from the given solution DataFrame.
    The solution DataFrame should have the following columns:
    - uld_idx: The index of the ULD in which the package is placed
    - package_idx: The index of the package
    - x: The x-coordinate of the package in the ULD
    - y: The y-coordinate of the package in the ULD
    - z: The z-coordinate of the package in the ULD
    """

    package_data = pd.read_csv(
        package_file,
        header=0,
        names=["package_id", "length", "width", "height", "weight", "priority", "cost"],
    )
    package_data["priority"] = package_data["priority"].apply(
        lambda x: 1 if x == "Priority" else 0
    )
    package_data["cost"] = package_data["cost"].apply(
        lambda x: 0 if x == "-" else int(x)
    )

    uld_df = pd.read_csv(
        uld_file,
        header=0,
        names=["uld_id", "length", "width", "height", "capacity"],
    )

    solution_df = pd.DataFrame(
        columns=["package_id", "uld_id", "x1", "y1", "z1", "x2", "y2", "z2"]
    )
    left_cost = 0
    priority_ulds = set()
    number_packages = 0

    for pack_idx, pack in package_data.iterrows():
        solution_row = df[df["package_idx"] == pack_idx]

        if solution_row.empty:
            solution_df = solution_df._append(
                {
                    "package_id": pack["package_id"],
                    "uld_id": "NONE",
                    "x1": -1,
                    "y1": -1,
                    "z1": -1,
                    "x2": -1,
                    "y2": -1,
                    "z2": -1,
                },
                ignore_index=True,
            )

            left_cost += pack["cost"]
        else:
            solution_row = solution_row.iloc[0]
            uld_id = uld_df.iloc[solution_row["uld_idx"]]["uld_id"]
            solution_df = solution_df._append(
                {
                    "package_id": pack["package_id"],
                    "uld_id": uld_id,
                    "x1": solution_row["x"],
                    "y1": solution_row["y"],
                    "z1": solution_row["z"],
                    "x2": solution_row["x"] + pack["length"],
                    "y2": solution_row["y"] + pack["width"],
                    "z2": solution_row["z"] + pack["height"],
                },
                ignore_index=True,
            )

            number_packages += 1
            if pack["priority"]:
                priority_ulds.add(uld_id)

    left_cost += len(priority_ulds) * priority_spread_cost

    with open(output_file, "w") as file:
        file.write(f"{left_cost} {number_packages} {len(priority_ulds)}\n")
        solution_df.to_csv(
            file,
            index=False,
            header=False,
        )
