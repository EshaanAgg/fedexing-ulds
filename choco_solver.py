from pychoco.model import Model

from utils import load_data, generate_solution_file
from validator import validate_solution


def solve_model(data):
    """
    Solves the package loading problem using PyChoco.
    """
    ulds = data["ULDs"]
    packages = data["packages"]

    count_uld = len(ulds)
    count_packages = len(packages)

    # Alternative to INF
    BIG_M = (
        max(uld["length"] for uld in ulds)
        + max(uld["width"] for uld in ulds)
        + max(uld["height"] for uld in ulds)
    )

    # Create model
    model = Model("Package Loading Problem")
    dims = ["length", "width", "height"]

    # Variables
    x = {}
    start = {}
    for i in range(count_packages):
        for j in range(count_uld):
            x[(i, j)] = model.boolvar(0, f"x_{i}_{j}")
            for d in dims:
                start[(i, j, d)] = model.intvar(0, BIG_M, f"start_{i}_{j}_{d}")

    # Constraints

    # Each package must be assigned to one ULD if priority, otherwise at most one ULD
    for i, package in enumerate(packages):
        if package["priority"]:
            model.sum([x[(i, j)] for j in range(count_uld)], "=", 1).post()
        else:
            model.sum([x[(i, j)] for j in range(count_uld)], "<=", 1).post()

    # Packages must fit within ULD dimensions
    for i, package in enumerate(packages):
        for j, uld in enumerate(ulds):
            for dim in dims:
                model.if_then(
                    x[(i, j)],
                    model.arithm(
                        start[(i, j, dim)], "+", (package[dim]), "<=", uld[dim]
                    ),
                )

    # for j in range(count_uld):
    #     for i1 in range(count_packages):
    #         for i2 in range(i1 + 1, count_packages):

    #             intersection_conditions = []

    #             for d in dims:
    #                 # x1 < x2 AND x2 < x1 + L1
    #                 c1 = model.arithm(start[(i1, j, d)], "<", start[(i2, j, d)])
    #                 c2 = model.arithm(
    #                     start[(i2, j, d)], "<", start[(i1, j, d)] + packages[i1][d]
    #                 )

    #             model.if_then(
    #                 x[(i1, j)] & x[(i2, j)],
    #                 model.and_(
    #                     [c1, c2],
    #                 ),
    #             )

    # ULD weight constraints
    for j, uld in enumerate(ulds):
        total_weight_vars = []

        for i in range(count_packages):
            weight_var = model.intvar(0, packages[i]["weight"], f"weight_{i}_{j}")
            model.times(x[(i, j)], packages[i]["weight"], weight_var).post()
            total_weight_vars.append(weight_var)

        model.sum(total_weight_vars, "<=", uld["capacity"]).post()

    # Objective: Minimize the cost of unshipped packages
    total_cost_vars = []

    for i in range(count_packages):
        for j in range(count_uld):
            # Define a binary variable for the shipped status (1 if shipped, 0 if not)
            shipped = x[(i, j)]  # This assumes x[(i, j)] is already a binary variable

            # Define the cost for each package based on the shipped status
            cost_var = model.intvar(0, packages[i]["cost"], f"cost_{i}_{j}")
            model.times(
                shipped, packages[i]["cost"], cost_var
            ).post()  # cost is added if shipped
            total_cost_vars.append(cost_var)

    # Sum the costs
    total_cost = model.intvar(0, 2000_000_000, "total_cost")
    model.sum(total_cost_vars, "=", total_cost).post()

    solver = model.get_solver()
    solution = solver.find_optimal_solution(
        total_cost,
        maximize=True,
    )

    # If solution is found, display the result
    if solution:
        print("Optimal solution found with total cost:", solver.get_objective_value())
    else:
        print("No solution found")

    # Extract solution
    if solution:
        print("Optimal solution found!")
        result = []
        for j in range(count_uld):
            for i in range(count_packages):
                if solution.get_int_val(x[(i, j)]) == 1:
                    result.append(
                        {
                            "uld_idx": j,
                            "package_idx": i,
                            "x": solution.get_int_val(start[(i, j)]["length"]),
                            "y": solution.get_int_val(start[(i, j)]["width"]),
                            "z": solution.get_int_val(start[(i, j)]["height"]),
                        }
                    )
        return result
    else:
        print("No optimal solution found!")
        return None


if __name__ == "__main__":
    data = load_data(load_frac=0.1)
    solution = solve_model(data)
    if solution is not None:
        solution.to_csv("./data/sol_cp_sat_raw.csv", index=False)
        generate_solution_file(solution, "./data/sol_cp_sat.csv")
        validate_solution("./data/sol_cp_sat.csv")
