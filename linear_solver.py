from ortools.linear_solver import pywraplp
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

    solver = pywraplp.Solver.CreateSolver("SCIP")
    if not solver:
        print("SCIP solver not found!")
        return

    # Alternative to INF
    BIG_M = (
        max(uld["width"] for uld in data["ULDs"])
        + max(uld["height"] for uld in data["ULDs"])
        + max(uld["length"] for uld in data["ULDs"])
    )

    # Variables
    # x[i, j] = 1 if package i is shipped in ULD j
    x = {}
    for i in range(count_packages):
        for j in range(count_uld):
            x[(i, j)] = solver.IntVar(0, 1, f"x_{i}_{j}")

    # pos[i, j, d] = position of package i in ULD j along dimension d
    pos = {}
    for i in range(count_packages):
        for j in range(count_uld):
            for d in range(3):
                pos[(i, j, d)] = solver.IntVar(0, BIG_M, f"pos_{i}_{j}_{d}")

    # Intersecting packages constraints
    # x1 + l1 > x2 AND x2 + l2 > x1 if enough to ensure that packages 1 and 2 intersect in the X dimension
    # Need to do this for all pairs of packages in all ULDs for all dimensions
    for j in range(count_uld):
        for i1, pack1 in enumerate(data["packages"]):
            for i2, pack2 in enumerate(data["packages"]):
                if i1 <= i2:
                    continue

                cond_vars = [solver.BoolVar(f"{i1}{i2}{j}_{k}") for k in range(6)]
                idx = 0

                for dim_idx, dim in enumerate(["length", "width", "height"]):
                    solver.Add(
                        pos[(i1, j, dim_idx)] + pack1[dim] >= pos[(i2, j, dim_idx)]
                    ).EnforceOnlyIf(cond_vars[idx])
                    idx += 1

                    solver.Add(
                        pos[(i2, j, dim_idx)] + pack2.get(dim) >= pos[(i1, j, dim_idx)]
                    ).EnforceOnlyIf(cond_vars[idx])
                    idx += 1

                solver.AddBoolAnd(cond_vars).OnlyEnforceIf(
                    x[(i1, j)] == 1,
                    x[(i2, j)] == 1,
                )

    # Other constraints
    for i, package in enumerate(data["packages"]):
        # Sum of x[i] for all ULDs must be 1 for priority packages
        # and 0 or 1 for non-priority packages (i.e., they can be shipped in at most one ULD)
        if package["priority"]:
            solver.Add(solver.Sum(x[i, j] for j in range(count_uld)) == 1)
        else:
            solver.Add(solver.Sum(x[i, j] for j, _ in range(count_uld)) <= 1)

        # Packages must fit entirely within the ULD dimensions
        for j, uld in enumerate(data["ULDs"]):
            for dimension, attribute in enumerate(["length", "width", "height"]):
                solver.Add(
                    (pos[(i, j, dimension)] + package[attribute]) <= uld[dimension]
                ).OnlyEnforceIf(x[i, j] == 1)

    # Total weight in each ULD must not exceed its capacity
    for j in range(count_uld):
        solver.Add(
            solver.Sum(
                x[i, j] * data["packages"][i]["weight"] for i in range(count_packages)
            )
            <= data["ULDs"][j]["capacity"]
        )

    # Objective: Minimize the cost of the unshipped packages
    solver.Minimize(solver.Sum(data["packages"][i]["cost"] * (1 - x[i, j])))
    # We will count each package once for each ULD it is not shipped in
    # Doesn't change the true objective as anyhow each package can be shipped in only one ULD

    # Solve
    status = solver.Solve()
    if status == pywraplp.Solver.OPTIMAL:
        print("Optimal solution found!")
        print("Packages shipped and their ULDs:")
        for j, _ in enumerate(data["ULDs"]):
            uld_packages = [
                i
                for i, _ in enumerate(data["packages"])
                if x[i, j].solution_value() > 0.5
            ]
            if uld_packages:
                print(f"ULD {j} contains packages: {uld_packages}")
        print()

        print("Packages not shipped:")
        not_shipped = [
            i for i, _ in enumerate(data["packages"]) if y[i].solution_value() < 0.5
        ]
        print(not_shipped)
        print()
        print("Total cost of shipped packages:", solver.Objective().Value())
        print("Time = ", solver.WallTime(), "ms")
    else:
        print("The problem does not have an optimal solution.")


if __name__ == "__main__":
    main()
