import time
import random
import pandas as pd
from typing import Optional, List
from collections import defaultdict

from models import Package, ULD, FFDecr, ConstructiveHeuristic


class Packer:
    def __init__(
        self,
        package_src: str,
        uld_src: str,
        first_fit_decr: FFDecr = FFDecr.VOLUME,
        constructive_heuristic: ConstructiveHeuristic = ConstructiveHeuristic.COLUMN,
        optimize_balance: bool = True,
        cpu_limit=10 * 60,
        front_side_support: bool = False,
        package_constraints: Optional[str] = None,
        uld_constraints: Optional[str] = None,
    ):
        """
        Initialize the packer with the packages and ULDs.
        """
        self.packages: List[Package] = Package.load_from_df(package_src)
        self.ulds: List[ULD] = ULD.load_from_df(uld_src)

        self.package_idx = {p.id: idx for idx, p in enumerate(self.packages)}
        self.uld_idx = {u.id: idx for idx, u in enumerate(self.ulds)}

        print(f"[INFO] Loaded {len(self.packages)} packages and {len(self.ulds)} ULDs.")

        self.first_fit_decr = first_fit_decr
        self.heuristic = constructive_heuristic
        self.optimize_balance = optimize_balance
        self.cpu_limit = cpu_limit
        self.front_side_support = front_side_support

        self.pack_constraints = self.load_pack_constraints(package_constraints)
        self.uld_constraints = self.load_uld_constraints(uld_constraints)

        # Step 1: Fix the order of the packages to process
        # Container order is assumed to be fixed
        self.pack_order = []
        self.sort_item()

        # Step 2: Run the constructive heuristic
        self.constructive_heuristic()
        self.best_solution = self.generate_solution_dataframe()
        self.best_metrics = self.get_metrics()

        # Step 3: Run the improvement heuristic
        # self.improvement_heuristic(0.8, 0.2)

    def sort_item(self):
        """
        Sort the packages based on the heuristic selected.
        """
        mx_weight = max(p.weight for p in self.packages) + 1
        mx_volume = max(p.volume for p in self.packages) + 1

        non_priority_pkgs = [p for p in self.packages if not p.priority]
        non_priority_pkgs.sort(
            key=lambda x: x.cost / x.volume,
            reverse=True,
        )

        priority_pkgs = [p for p in self.packages if p.priority]
        if self.first_fit_decr == FFDecr.VOLUME:
            priority_pkgs.sort(
                key=lambda x: x.volume * mx_volume + x.weight,
                reverse=True,
            )

        elif self.first_fit_decr == FFDecr.WEIGHT:
            priority_pkgs.sort(
                key=lambda x: x.weight * mx_weight + x.volume,
                reverse=True,
            )

        elif self.first_fit_decr == FFDecr.MAX_DIM:
            priority_pkgs.sort(
                key=lambda x: x.mx_dim * mx_volume + x.volume,
                reverse=True,
            )

        print(
            "[INFO] Priority packages:",
            len(priority_pkgs),
            "| Non-priority packages:",
            len(non_priority_pkgs),
        )
        self.pack_order = priority_pkgs + non_priority_pkgs

    def load_solution(self, solution_data):
        """
        Loads the stored solution into the packer.
        This method is needed in the improvement heuristic.
        """

        for idx in range(len(self.packages)):
            self.packages[idx].reset()
        for idx in range(len(self.ulds)):
            self.ulds[idx].reset()

        for row in solution_data:
            uld_idx = self.uld_idx[row["uld_id"]]
            pack_idx = self.package_idx[row["pack_id"]]
            x1, y1, z1 = row["x1"], row["y1"], row["z1"]
            x2, y2, z2 = row["x2"], row["y2"], row["z2"]

            self.ulds[uld_idx].add_package(
                self.packages[pack_idx], pack_idx, (x1, y1, z1), (x2, y2, z2)
            )
            self.packages[pack_idx].place_in_uld(uld_idx, (x1, y1, z1), (x2, y2, z2))

    def improve_solution(self, lambda_probability: float):
        """
        Tries to improve on the current solution by repacking the packages.
        """
        cur_time = time.time()
        iteration_count = 0

        while time.time() - cur_time < self.cpu_limit / 2:
            iteration_count += 1
            rnd = random.random()
            if rnd < lambda_probability:
                self.load_solution(self.best_solution)

            # Shuffle the packages and the orientations
            random.shuffle(self.pack_order)
            for pack in self.packages:
                random.shuffle(pack.orients)

            removed_packages = []

            for container_idx in range(len(self.ulds)):
                uld = self.ulds[container_idx]
                initial_volume_usage = uld.packed_volume / uld.volume
                curr_removed_packages = []

                # Empty the container
                for pack_idx in uld.package_idx:
                    removed_packages.append(pack_idx)
                    curr_removed_packages.append(pack_idx)
                    self.packages[pack_idx].reset()
                uld.reset()

                rnd = random.random()
                if rnd > (1 - initial_volume_usage) / 2:
                    # Pack some of the removed packages in the same order
                    for pack_idx in curr_removed_packages:
                        rnd = random.random()
                        if rnd < 0.5:
                            continue

                        if self.add_pack_to_uld(pack_idx, container_idx):
                            removed_packages.remove(pack_idx)

            self.constructive_heuristic(removed_packages)
        print(f"[INFO] Iteration {iteration_count} completed.")

    def improvement_heuristic(
        self, lambda_probability: float, gamma_probability: float
    ):
        self.improve_solution(lambda_probability)

        self.best_solution = self.generate_solution_dataframe()
        self.best_metrics = self.get_metrics()

    def add_pack_to_uld(self, packIdx: int, uldIdx: int) -> bool:
        """
        Tries to add a package to a ULD. Returns True if successful.
        """
        uld = self.ulds[uldIdx]
        pack = self.packages[packIdx]

        # Feasibility checks
        if uldIdx in self.uld_constraints[packIdx]:
            return False
        for other_pack in uld.package_idx:
            if packIdx in self.pack_constraints[other_pack]:
                return False

        if (
            uld.packed_volume + pack.volume > uld.volume
            or uld.packed_weight + pack.weight > uld.weight
        ):
            return False

        min_x = uld.x
        min_y = uld.y
        min_z = uld.z
        candidate_orient = None
        candidate_corners = None

        # Check all the orientations
        for orient in pack.orients:

            # Check all the reference points
            for ref_pt in uld.ref_pts:
                origin_x, origin_y, origin_z = ref_pt

                # Heavy packages should be placed at the bottom
                if pack.heavy and origin_y > 0:
                    continue

                corners = Packer.get_coords_based_on_orient(
                    pack.x, pack.y, pack.z, origin_x, origin_y, origin_z, orient
                )
                opp_x, opp_y, opp_z = corners[-1]
                if uld.out_of_bounds(opp_x, opp_y, opp_z):
                    continue

                # Check for intersection with already placed packages
                valid = True
                for pack_idx in uld.package_idx:
                    if (
                        self.packages[pack_idx].get_intersection_volume(
                            origin_x, origin_y, origin_z, opp_x, opp_y, opp_z
                        )
                        != 0
                    ):
                        valid = False
                        break
                if not valid:
                    continue

                # TODO: To add bottom area intersection placement condition
                # TODO: Add front side support condition validation here

                if self.heuristic == ConstructiveHeuristic.WALL:
                    if (
                        origin_z < min_z
                        or (origin_z == min_z and origin_y < min_y)
                        or (
                            origin_z == min_z and origin_y == min_y and origin_x < min_x
                        )
                    ):
                        min_x = origin_x
                        min_y = origin_y
                        min_z = origin_z
                        candidate_orient = orient
                        candidate_corners = corners

                elif self.heuristic == ConstructiveHeuristic.LAYER:
                    if (
                        origin_y < min_y
                        or (origin_y == min_y and origin_z < min_z)
                        or (
                            origin_y == min_y and origin_z == min_z and origin_x < min_x
                        )
                    ):
                        min_x = origin_x
                        min_y = origin_y
                        min_z = origin_z
                        candidate_orient = orient
                        candidate_corners = corners

                elif self.heuristic == ConstructiveHeuristic.COLUMN:
                    if (
                        origin_x < min_x
                        or (origin_x == min_x and origin_y < min_y)
                        or (
                            origin_x == min_x and origin_y == min_y and origin_z < min_z
                        )
                    ):
                        min_x = origin_x
                        min_y = origin_y
                        min_z = origin_z
                        candidate_orient = orient
                        candidate_corners = corners

                else:
                    raise ValueError(f"Invalid heuristic {self.heuristic}")

        if candidate_orient is None:
            return False

        uld.add_package(pack, packIdx, candidate_corners[0], candidate_corners[-1])
        pack.place_in_uld(uldIdx, candidate_corners[0], candidate_corners[-1])

        return True

    def constructive_heuristic(
        self, packages: Optional[List[int]] = None, ulds: Optional[List[int]] = None
    ):
        """
        Run the constructive heuristic to pack the packages.
        """

        if packages is None:
            packages = [self.package_idx[p.id] for p in self.pack_order]
        if ulds is None:
            ulds = range(len(self.ulds))

        for pack_idx in packages:
            for uld_idx in ulds:
                if self.add_pack_to_uld(pack_idx, uld_idx):
                    break

    # Helper functions
    def get_coords_based_on_orient(x, y, z, org_x, org_y, org_z, orient):
        """
        Get the coordinates of the package based on the orientation.
        """

        def get(ch):
            if ch == "x":
                return x
            elif ch == "y":
                return y
            elif ch == "z":
                return z

        pts = []
        for mask in range(0, 8):
            xn = org_x + (mask & 1) * get(orient[0])
            yn = org_y + (mask & (1 << 1)) * get(orient[1])
            zn = org_z + (mask & (1 << 2)) * get(orient[2])

            pts.append((xn, yn, zn))

        return pts

    def load_pack_constraints(self, file: Optional[str]) -> dict:
        """
        Load constraints from a CSV file.
        """
        constraints = defaultdict(lambda: set())
        if file is None:
            return constraints

        df = pd.read_csv(file, columns=["id1", "id2"])

        for _, row in df.iterrows():
            if row["id1"] not in self.package_idx:
                raise ValueError(f"Package {row['id1']} not found.")
            if row["id2"] not in self.package_idx:
                raise ValueError(f"Package {row['id2']} not found.")

            idx1 = self.package_idx[row["id1"]]
            idx2 = self.package_idx[row["id2"]]

            constraints[idx1].add(idx2)
            constraints[idx2].add(idx1)

        return constraints

    def load_uld_constraints(self, file: Optional[str]) -> dict:
        """
        Load constraints from a CSV file.
        """
        constraints = defaultdict(lambda: set())
        if file is None:
            return constraints

        df = pd.read_csv(file, columns=["pack_id", "uld_id"])

        for _, row in df.iterrows():
            if row["pack_id"] not in self.package_idx:
                raise ValueError(f"Package {row['pack_id']} not found.")
            if row["uld_id"] not in self.uld_idx:
                raise ValueError(f"ULD {row['uld_id']} not found.")

            idx1 = self.package_idx[row["pack_id"]]
            idx2 = self.uld_idx[row["uld_id"]]

            constraints[idx1].add(idx2)

        return constraints

    def get_metrics(self):
        """
        Get the incumbent metrics.
        """
        packed_volume = sum(uld.packed_volume for uld in self.ulds)
        packed_weight = sum(uld.packed_weight for uld in self.ulds)
        packed_score = sum(
            self.packages[idx].cost for uld in self.ulds for idx in uld.package_idx
        )
        packed_cnt = sum(1 for uld in self.ulds for idx in uld.package_idx)

        total_volume = sum(uld.volume for uld in self.ulds)
        total_weight = sum(uld.weight for uld in self.ulds)
        total_package_score = sum(p.cost for p in self.packages)
        utilization = sum(
            max(uld.packed_volume / uld.volume, uld.packed_weight / uld.weight)
            for uld in self.ulds
        )

        return {
            "packed_cnt": packed_cnt,
            "volume_utilization": packed_volume / total_volume,
            "weight_utilization": packed_weight / total_weight,
            "score_utilization": packed_score / total_package_score,
            "utilization": utilization,
            "dispersion": sum(1 if uld.has_priority else 0 for uld in self.ulds),
        }

    def generate_solution_dataframe(self):
        """
        Generate the solution dataframe.
        """
        data = []
        for uld in self.ulds:
            for idx in uld.package_idx:
                pack: Package = self.packages[idx]
                data.append(
                    {
                        "uld_id": uld.id,
                        "pack_id": pack.id,
                        "x1": pack.pt1[0],
                        "y1": pack.pt1[1],
                        "z1": pack.pt1[2],
                        "x2": pack.pt2[0],
                        "y2": pack.pt2[1],
                        "z2": pack.pt2[2],
                    }
                )

        return data
