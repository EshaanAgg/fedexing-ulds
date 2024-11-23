from ortools.sat.python import cp_model
import pandas as pd

from utils import load_data, generate_solution_file
from validator import validate_solution


def solve_model(data):
    """
    Solves the model for the given data and returns the solution.
    """
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
    # x[i, j] = 1 if package i is shipped in ULD j
    x = {}
    for i in range(count_packages):
        for j in range(count_uld):
            x[(i, j)] = model.NewIntVar(0, 1, f"x_{i}_{j}")

    # start[i, j, d] = position of package i in ULD j along dimension d
    start = {}
    interval = {}
    for i, pack in enumerate(data["packages"]):
        for j in range(count_uld):
            for d, dim in enumerate(["length", "width", "height"]):
                start[(i, j, d)] = model.NewIntVar(0, BIG_M, f"start_{i}_{j}_{d}")
                interval[(i, j, d)] = model.NewOptionalIntervalVar(
                    start[(i, j, d)],
                    pack[dim],
                    start[(i, j, d)] + pack[dim],
                    x[(i, j)],
                    f"interval_{i}_{j}_{d}",
                )

    # Constraints: Packages cannot intersect in the same ULD
    # Intersect -> (x1 < x2 AND x2 < x1 + L1) OR (x2 < x1 AND x1 < x2 + L2)

    for j in range(count_uld):
        for i1, pack1 in enumerate(data["packages"]):
            for i2, pack2 in enumerate(data["packages"]):
                if i1 >= i2:
                    continue

            # bv = [model.NewBoolVar(f"{i1}_{i2}_{j}_{k}") for k in range(9)]

            # # x1 < x2
            # model.Add(start[(i1, j, 2)] < start[(i2, j, 2)]).OnlyEnforceIf(bv[0])

            # # x2 < x1 + L1
            # model.Add(
            #     start[(i2, j, 2)] < start[(i1, j, 2)] + pack1["height"]
            # ).OnlyEnforceIf(bv[1])

            # # bv[2] -> AND of bv[0] and bv[1]
            # model.AddBoolAnd([bv[0], bv[1]]).OnlyEnforceIf(bv[2])

            # # x2 < x1
            # model.Add(start[(i2, j, 2)] < start[(i1, j, 2)]).OnlyEnforceIf(bv[3])

            # # x1 < x2 + L2
            # model.Add(
            #     start[(i1, j, 2)] < start[(i2, j, 2)] + pack2["height"]
            # ).OnlyEnforceIf(bv[4])

            # # bv[5] -> AND of bv[3] and bv[4]
            # model.AddBoolAnd([bv[3], bv[4]]).OnlyEnforceIf(bv[5])

            # # bv[6] -> Intersection condition (bv[6] = bv[2] OR bv[5])
            # model.AddBoolOr([bv[2], bv[5]]).OnlyEnforceIf(bv[6])

            # # bv[7] -> Both in the same ULD
            # model.Add(x[(i1, j)] + x[(i2, j)] == 2).OnlyEnforceIf(bv[7])

            # # bv[8] -> bv[6] AND bv[7] -> Intersect in Z and in same ULD
            # model.AddBoolAnd([bv[6], bv[7]]).OnlyEnforceIf(bv[8])

            # # Ensure that no overlap in other dimensions if bv[8]
            # model.AddNoOverlap2D(
            #     [interval[(i1, j, 0)], interval[(i2, j, 0)]],
            #     [interval[(i1, j, 1)], interval[(i2, j, 1)]],
            # ).OnlyEnforceIf(bv[8])

            bv = [model.NewBoolVar(f"{i1}_{i2}_{j}_{k}") for k in range(4)]

            # bv[0]: Both packages are in the same unit
            model.Add(x[(i1, j)] + x[(i2, j)] == 2).OnlyEnforceIf(bv[0])

            # bv[1]: Ensure no overlap in the X dimension
            model.Add(
                start[(i1, j, 0)] + pack1["length"] <= start[(i2, j, 0)]
            ).OnlyEnforceIf(
                bv[1]
            )  # i1 ends before i2 starts
            model.Add(
                start[(i2, j, 0)] + pack2["length"] <= start[(i1, j, 0)]
            ).OnlyEnforceIf(
                bv[1]
            )  # i2 ends before i1 starts

            # bv[2]: Ensure no overlap in the Y dimension
            model.Add(
                start[(i1, j, 1)] + pack1["width"] <= start[(i2, j, 1)]
            ).OnlyEnforceIf(
                bv[2]
            )  # i1 ends before i2 starts
            model.Add(
                start[(i2, j, 1)] + pack2["width"] <= start[(i1, j, 1)]
            ).OnlyEnforceIf(
                bv[2]
            )  # i2 ends before i1 starts

            # bv[3]: Ensure no overlap in the Z dimension
            model.Add(
                start[(i1, j, 2)] + pack1["height"] <= start[(i2, j, 2)]
            ).OnlyEnforceIf(
                bv[3]
            )  # i1 ends before i2 starts
            model.Add(
                start[(i2, j, 2)] + pack2["height"] <= start[(i1, j, 2)]
            ).OnlyEnforceIf(
                bv[3]
            )  # i2 ends before i1 starts

            # Combine all conditions: no overlap in X, Y, or Z if both are placed in the same unit
            model.AddBoolAnd([bv[1], bv[2], bv[3]]).OnlyEnforceIf(bv[0])

            # Ensure non-overlap in 3D when both are in the same unit
            model.AddImplication(bv[0], bv[1])  # No X overlap if in same unit
            model.AddImplication(bv[0], bv[2])  # No Y overlap if in same unit
            model.AddImplication(bv[0], bv[3])  # No Z overlap if in same unit

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
                    start[(i, j, dim_idx)] + package[dim] <= uld[dim]
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
    # We will count each package once for each ULD it is not shipped in
    # Doesn't change the true objective as anyhow each package can be shipped in only one ULD
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

    df = pd.DataFrame(columns=["uld_idx", "package_idx", "x", "y", "z"])

    if status == cp_model.OPTIMAL:
        print("Optimal solution found!")
        for j in range(count_uld):
            for i in range(count_packages):
                if solver.Value(x[(i, j)]) == 1:
                    df = df._append(
                        {
                            "uld_idx": j,
                            "package_idx": i,
                            "x": solver.Value(start[(i, j, 0)]),
                            "y": solver.Value(start[(i, j, 1)]),
                            "z": solver.Value(start[(i, j, 2)]),
                        },
                        ignore_index=True,
                    )

        return df
    else:
        print("No optimal solution found!")
        return None


if __name__ == "__main__":
    data = load_data(load_frac=0.2)
    solution = solve_model(data)

    if solution is not None:
        solution.to_csv("./data/sol_cp_sat_raw.csv", index=False)
        generate_solution_file(solution, "./data/sol_cp_sat.csv")
        validate_solution("./data/sol_cp_sat.csv")
