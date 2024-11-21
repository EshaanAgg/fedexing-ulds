from ortools.sat.python import cp_model
import pandas as pd


def load_data():
    data = {}

    uld_data = pd.read_csv(
        "ulds.csv",
        header=0,
        names=["id", "length", "width", "height", "capacity"],
    )

    package_data = pd.read_csv(
        "packages.csv",
        header=0,
        names=["id", "length", "width", "height", "weight", "priority", "cost"],
    )
    package_data["priority"] = package_data["priority"].apply(
        lambda x: True if x == "Priority" else False
    )
    package_data["cost"] = package_data["cost"].apply(
        lambda x: 1e9 if x == "-" else int(x)
    )

    data["ULDs"] = uld_data.to_dict(orient="records")
    data["packages"] = package_data.to_dict(orient="records")

    return data


def main():
    data = load_data()

    count_uld = len(data["ULDs"])
    count_packages = len(data["packages"])

    model = cp_model.CpModel()

    # Alternative to INF
    BIG_M = (
        max(uld["width"] for uld in data["ULDs"])
        + max(uld["height"] for uld in data["ULDs"])
        + max(uld["length"] for uld in data["ULDs"])
    )

    # Variables
    x = {}
    for i in range(count_packages):
        for j in range(count_uld):
            x[(i, j)] = model.NewIntVar(0, 1, f"x_{i}_{j}")

    pos = {}
    for i in range(count_packages):
        for j in range(count_uld):
            for d in range(3):
                pos[(i, j, d)] = model.NewIntVar(0, BIG_M, f"pos_{i}_{j}_{d}")

    # Constraints: Packages cannot intersect in the same ULD
    for j in range(count_uld):
        for i1, pack1 in enumerate(data["packages"]):
            for i2, pack2 in enumerate(data["packages"]):
                if i1 >= i2:
                    continue

                cond_vars = [model.NewBoolVar(f"{i1}_{i2}_{j}_{k}") for k in range(6)]
                idx = 0

                for dim_idx, dim in enumerate(["length", "width", "height"]):
                    model.Add(
                        pos[(i1, j, dim_idx)] + pack1[dim] >= pos[(i2, j, dim_idx)]
                    ).OnlyEnforceIf(cond_vars[idx])
                    idx += 1

                    model.Add(
                        pos[(i2, j, dim_idx)] + pack2.get(dim) >= pos[(i1, j, dim_idx)]
                    ).OnlyEnforceIf(cond_vars[idx])
                    idx += 1

                same_box_check = model.NewBoolVar(f"{i1}_{i2}_{j}")
                model.Add(x[(i1, j)] + x[(i2, j)] == 2).OnlyEnforceIf(same_box_check)
                model.AddBoolAnd(cond_vars).OnlyEnforceIf(same_box_check)

    # Other constraints
    for i, package in enumerate(data["packages"]):
        # Sum of x[i] for all ULDs must be 1 for priority packages
        # and 0 or 1 for non-priority packages
        if package["priority"]:
            model.Add(sum(x[(i, j)] for j in range(count_uld)) == 1)
        else:
            model.Add(sum(x[(i, j)] for j in range(count_uld)) <= 1)

        # Packages must fit entirely within the ULD dimensions
        for j, uld in enumerate(data["ULDs"]):
            for dim_idx, dim in enumerate(["length", "width", "height"]):
                model.Add(
                    pos[(i, j, dim_idx)] + package[dim] <= uld[dim]
                ).OnlyEnforceIf(x[(i, j)])

    # Total weight in each ULD must not exceed its capacity
    for j in range(count_uld):
        model.Add(
            sum(
                x[(i, j)] * data["packages"][i]["weight"] for i in range(count_packages)
            )
            <= data["ULDs"][j]["capacity"]
        )

    # Objective: Minimize the cost of the unshipped packages
    model.Minimize(
        sum(
            data["packages"][i]["cost"] * (1 - x[(i, j)])
            for i in range(count_packages)
            for j in range(count_uld)
        )
    )

    print(f"Model created successfully!\n")

    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    if status == cp_model.OPTIMAL:
        print("Optimal solution found!")
        print("Packages shipped and their ULDs:")
        for j in range(count_uld):
            uld_packages = [
                i for i in range(count_packages) if solver.Value(x[(i, j)]) == 1
            ]
            if uld_packages:
                print(f"ULD {j} contains packages: {uld_packages}")
        print()
        print("Objective value:", solver.ObjectiveValue())
    else:
        print("The problem does not have an optimal solution.")


if __name__ == "__main__":
    main()
