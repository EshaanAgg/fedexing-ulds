import numpy as np
import pandas as pd


def compute_space(
    solution_path: str,
):
    package_data = pd.read_csv(
        solution_path,
        header=0,
        names=[
            "uld_id",
            "pack_id",
            "x1",
            "y1",
            "z1",
            "x2",
            "y2",
            "z2",
        ],
    )

    # Group by uld_id and iterate over each group
    for uld_id, df in package_data.groupby("uld_id"):
        tot_volume = 0
        tot_pack_volume = 0

        for _, row in df.iterrows():
            tot_pack_volume += (
                (row["x2"] - row["x1"])
                * (row["y2"] - row["y1"])
                * (row["z2"] - row["z1"])
            )

            nearest_to_f1 = [
                [np.inf for _ in range(row["y1"], row["y2"] + 1)]
                for _ in range(row["z1"], row["z2"] + 1)
            ]
            nearest_to_f2 = [
                [np.inf for _ in range(row["y1"], row["y2"] + 1)]
                for _ in range(row["z1"], row["z2"] + 1)
            ]
            nearest_to_f3 = [
                [np.inf for _ in range(row["x1"], row["x2"] + 1)]
                for _ in range(row["z1"], row["z2"] + 1)
            ]
            nearest_to_f4 = [
                [np.inf for _ in range(row["x1"], row["x2"] + 1)]
                for _ in range(row["z1"], row["z2"] + 1)
            ]

            for _, pack2 in df.iterrows():
                if pack2["pack_id"] == row["pack_id"]:
                    continue

                min_x = max(row["x1"], pack2["x1"])
                max_x = min(row["x2"], pack2["x2"])
                min_y = max(row["y1"], pack2["y1"])
                max_y = min(row["y2"], pack2["y2"])
                min_z = max(row["z1"], pack2["z1"])
                max_z = min(row["z2"], pack2["z2"])

                for y in range(min_y, max_y + 1):
                    for z in range(min_z, max_z + 1):
                        if pack2["x2"] <= row["x1"]:
                            nearest_to_f1[z - row["z1"]][y - row["y1"]] = min(
                                nearest_to_f1[z - row["z1"]][y - row["y1"]],
                                row["x1"] - pack2["x2"],
                            )
                        elif pack2["x1"] >= row["x2"]:
                            nearest_to_f2[z - row["z1"]][y - row["y1"]] = min(
                                nearest_to_f2[z - row["z1"]][y - row["y1"]],
                                pack2["x1"] - row["x2"],
                            )

                for x in range(min_x, max_x + 1):
                    for z in range(min_z, max_z + 1):
                        if pack2["y2"] <= row["y1"]:
                            nearest_to_f3[z - row["z1"]][x - row["x1"]] = min(
                                nearest_to_f3[z - row["z1"]][x - row["x1"]],
                                row["y1"] - pack2["y2"],
                            )
                        elif pack2["y1"] >= row["y2"]:
                            nearest_to_f4[z - row["z1"]][x - row["x1"]] = min(
                                nearest_to_f4[z - row["z1"]][x - row["x1"]],
                                pack2["y1"] - row["y2"],
                            )

            for y in range(row["y1"], row["y2"] + 1):
                for z in range(row["z1"], row["z2"] + 1):
                    idx1 = y - row["y1"]
                    idx2 = z - row["z1"]
                    if nearest_to_f1[idx2][idx1] is not np.inf:
                        tot_volume += nearest_to_f1[idx2][idx1]
                    if nearest_to_f2[idx2][idx1] is not np.inf:
                        tot_volume += nearest_to_f2[idx2][idx1]

            for x in range(row["x1"], row["x2"] + 1):
                for z in range(row["z1"], row["z2"] + 1):
                    idx1 = x - row["x1"]
                    idx2 = z - row["z1"]
                    if nearest_to_f3[idx2][idx1] is not np.inf:
                        tot_volume += nearest_to_f3[idx2][idx1]
                    if nearest_to_f4[idx2][idx1] is not np.inf:
                        tot_volume += nearest_to_f4[idx2][idx1]

        tot_volume /= 2

        print(
            "ULD ID:",
            uld_id,
            "| Cushion Vol: ",
            tot_volume,
            "| Total pack volume: ",
            tot_pack_volume,
            "| Frac: ",
            tot_volume / tot_pack_volume,
        )


if __name__ == "__main__":
    compute_space("./soln_for_viz.csv")
