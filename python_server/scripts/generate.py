import sys
import time
import pandas as pd

if __name__ == "__main__":
    args = sys.argv[1:]
    package_path = args[0]
    uld_path = args[1]
    solution_path = args[2]

    time.sleep(40)

    # Copy the sample solution file to the solution path
    df = pd.read_csv("./data/sample_solution.csv")
    df.to_csv(solution_path, index=False)
