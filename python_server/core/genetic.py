import copy
import random
import numpy as np
import pandas as pd
from typing import List


PENALTY_COST = 10000000
COST_PER_ULD = 5000


def check_intersection_cuboids(a0, a1, b0, b1):
    dx = min(a1[0], b1[0]) - max(a0[0], b0[0])
    dy = min(a1[1], b1[1]) - max(a0[1], b0[1])
    dz = min(a1[2], b1[2]) - max(a0[2], b0[2])
    if dx <= 0 or dy <= 0 or dz <= 0:
        return False
    return True


directs = [
    [0, 0, 0],
    [0, 0, 0],
    [0, -1, 0],
    [-1, 0, 0],
    [-1, -1, 0],
    [0, 0, -1],
    [0, -1, -1],
    [-1, 0, -1],
    [-1, -1, -1],
]


class Config:
    def __init__(self, all_pkgs, all_ulds):
        self.priority_order = []
        self.non_priority_order = []
        self.enc_priority_ord = []
        self.enc_non_priority_ord = []
        self.fitness_score = -1
        self.packages_placed = 0
        self.resultant_data = []
        self.priority_packed = 0
        self.non_priority_packed = 0
        self.ulds_used_for_priority = 0
        self.evaluated = False
        self.uld_wts = []

        self.all_pkgs = all_pkgs
        self.all_ulds = all_ulds

        # Calculate other parameters
        self.count_priority_pkg = sum([pkg.priority for pkg in all_pkgs])
        self.count_non_priority_pkg = len(all_pkgs) - self.count_priority_pkg
        self.priority_idx = [i for i, pkg in enumerate(all_pkgs) if pkg.priority]
        self.non_priority_idx = [
            i for i, pkg in enumerate(all_pkgs) if not pkg.priority
        ]

        for _ in range(len(all_ulds)):
            self.uld_wts.append(0)

    def initialize(self):
        """
        Initialize the configuration with random values
        """
        self.enc_priority_ord = np.random.uniform(
            low=0.0,
            high=1.0,
            size=self.count_priority_pkg,
        )
        self.enc_non_priority_ord = np.random.uniform(
            low=0.0,
            high=1.0,
            size=self.count_non_priority_pkg,
        )

    def decode(self):
        """
        Decodes the encoded values to get the order of the packages
        """
        relative_p_order = np.argsort(self.enc_priority_ord)
        relative_non_p_order = np.argsort(self.enc_non_priority_ord)

        for i in relative_p_order:
            self.priority_order.append(self.priority_idx[i])

        for i in relative_non_p_order:
            self.non_priority_order.append(self.non_priority_idx[i])

    def print_config(self):
        """
        Prints the configuration [for debugging purposes]
        """
        self.fitness_score = self.find_fitness()

        print("Score:", self.fitness_score)
        print("Total package: ", len(self.resultant_data))
        print("Priority Order: ", self.priority_order)
        print("Economy Order: ", self.non_priority_order)

    def reset_uld_points(self):
        """
        Resets the ULD points, so that the packages can be placed again
        from the start
        """
        uld_pts = []
        for i in range(len(self.all_ulds)):
            uld_pts.append([])

        for obj in self.resultant_data:
            uid = obj[1]
            a = obj[5] - obj[2]
            b = obj[6] - obj[3]
            c = obj[7] - obj[4]
            x = obj[2]
            y = obj[3]
            z = obj[4]
            args = [
                [0, 0, 0],
                [a, 0, 0],
                [0, b, 0],
                [0, 0, c],
                [a, b, 0],
                [a, 0, c],
                [0, b, c],
                [a, b, c],
            ]

            for i in range(8):
                num = i + 1
                for j in range(8):
                    uld_pts[uid].append(
                        [x + args[j][0], y + args[j][1], z + args[j][2], num]
                    )

        for obj in self.all_ulds:
            uid = obj.id
            uld_pts[uid].append([0, 0, 0, 1])
            uld_pts[uid].append([obj.length, 0, 0, 3])
            uld_pts[uid].append([0, obj.width, 0, 2])
            uld_pts[uid].append([obj.length, obj.width, 0, 4])
            uld_pts[uid].append([0, 0, obj.height, 5])
            uld_pts[uid].append([obj.length, 0, obj.height, 7])
            uld_pts[uid].append([0, obj.width, obj.height, 6])
            uld_pts[uid].append([obj.length, obj.width, obj.height, 8])

        return uld_pts

    def add_point(self, uid, x, y, z, a, b, c, uld_pts):
        """
        Adds the reference points to the ULD points
        for the given ULD, so that the packages can be
        placed in the ULD
        """
        args = [
            [0, 0, 0],
            [a, 0, 0],
            [0, b, 0],
            [0, 0, c],
            [a, b, 0],
            [a, 0, c],
            [0, b, c],
            [a, b, c],
        ]
        for i in range(8):
            num = i + 1
            for j in range(8):
                uld_pts[uid].append(
                    [x + args[j][0], y + args[j][1], z + args[j][2], num]
                )

    def final_checker(self, uid, pt_of_place, orientation, pid):
        """
        Checks the final condition for placing the package in the ULD
        - Weight should be less than the weight capacity of the ULD
        - The package should not intersect with any other package
        - The package should be placed within the ULD

        Returns:
        - True if the package can be placed
        - False if the package cannot be placed
        """

        if (
            self.uld_wts[uid] + self.all_pkgs[pid].weight
            > (self.all_ulds[uid]).capacity
        ):
            return False
        if pt_of_place[0] + orientation[0] > self.all_ulds[uid].length:
            return False
        if pt_of_place[1] + orientation[1] > self.all_ulds[uid].width:
            return False
        if pt_of_place[2] + orientation[2] > self.all_ulds[uid].height:
            return False

        for ele in self.resultant_data:
            if ele[1] == uid:
                second_pt = [
                    pt_of_place[0] + orientation[0],
                    pt_of_place[1] + orientation[1],
                    pt_of_place[2] + orientation[2],
                ]
                if check_intersection_cuboids(
                    pt_of_place,
                    second_pt,
                    [ele[2], ele[3], ele[4]],
                    [ele[5], ele[6], ele[7]],
                ):
                    return False

        return True

    def place_priority(self, uld_pts):
        """
        Places all the priority packages in the ULDs
        specified by the ULD points in the priority order
        """
        for it in range(len(self.priority_order)):
            pid = (self.priority_order)[it]
            pckg = self.all_pkgs[pid]
            poss_pts = []
            a = pckg.length
            b = pckg.width
            c = pckg.height
            orient = [[a, b, c], [a, c, b], [b, a, c], [b, c, a], [c, a, b], [c, b, a]]

            for num in range(len(self.all_ulds)):
                uid = self.all_ulds[num]
                for ref_pt in uld_pts[uid]:
                    xx, yy, zz, dir_idx = ref_pt[0]

                    for args in orient:
                        xx = ref_pt[0] + (args[0] * directs[dir_idx][0])
                        yy = ref_pt[1] + (args[1] * directs[dir_idx][1])
                        zz = ref_pt[2] + (args[2] * directs[dir_idx][2])
                        if xx < 0 or yy < 0 or zz < 0:
                            continue

                        if self.final_checker(
                            uid, [xx, yy, zz], [args[0], args[1], args[2]], pid
                        ):
                            poss_pts.append(
                                [
                                    pid,
                                    uid,
                                    xx,
                                    yy,
                                    zz,
                                    args[0],
                                    args[1],
                                    args[2],
                                    dir_idx,
                                ]
                            )

            poss_pts = sorted(
                poss_pts,
                key=lambda x: (
                    -(len(uld_pts[x[1]])),
                    x[4],
                    (
                        abs(
                            min(x[2], (self.all_ulds[x[1]].length - x[2] - x[5]))
                            + min(x[3], (self.all_ulds[x[1]].width - x[3] - x[6]))
                        )
                    ),
                    (x[2] * x[2] + x[3] * x[3] + x[4] * x[4]),
                ),
            )

            if len(poss_pts) == 0:
                continue
            else:
                # Update the resultant data and the reference points
                # for the next package
                self.resultant_data.append(
                    [
                        poss_pts[0][0],
                        poss_pts[0][1],
                        poss_pts[0][2],
                        poss_pts[0][3],
                        poss_pts[0][4],
                        poss_pts[0][2] + poss_pts[0][5],
                        poss_pts[0][3] + poss_pts[0][6],
                        poss_pts[0][4] + poss_pts[0][7],
                    ]
                )

                self.uld_wts[poss_pts[0][1]] += pckg.weight

                x_t = poss_pts[0][2] - poss_pts[0][5] * directs[poss_pts[0][8]][0]
                y_t = poss_pts[0][3] - poss_pts[0][6] * directs[poss_pts[0][8]][1]
                z_t = poss_pts[0][4] - poss_pts[0][7] * directs[poss_pts[0][8]][2]

                # Remove the used reference points
                uld_pts[poss_pts[0][1]].remove([x_t, y_t, z_t, poss_pts[0][8]])

                # Add 3 more reference points
                self.add_point(
                    poss_pts[0][1],
                    x_t,
                    y_t,
                    z_t,
                    poss_pts[0][5],
                    poss_pts[0][6],
                    poss_pts[0][7],
                    uld_pts,
                )

    def place_economy(self, uld_pts):
        """
        Places all the non-priority packages in the ULDs
        specified by the ULD points in the non-priority order
        """
        for it in range(len(self.non_priority_order)):
            pid = self.non_priority_order[it]
            pckg = self.all_pkgs[pid]
            poss_pts = []
            a = pckg.length
            b = pckg.width
            c = pckg.height
            orient = [[a, b, c], [a, c, b], [b, a, c], [b, c, a], [c, a, b], [c, b, a]]

            for num in range(len(self.all_ulds)):
                uid = self.all_ulds[num]
                for ref_pt in uld_pts[uid]:
                    xx, yy, zz, dir_idx = ref_pt[0]
                    dir_idx = ref_pt[3]

                    for args in orient:
                        xx = ref_pt[0] + (args[0] * directs[dir_idx][0])
                        yy = ref_pt[1] + (args[1] * directs[dir_idx][1])
                        zz = ref_pt[2] + (args[2] * directs[dir_idx][2])
                        if xx < 0 or yy < 0 or zz < 0:
                            continue

                        if self.final_checker(
                            uid, [xx, yy, zz], [args[0], args[1], args[2]], pid
                        ):
                            poss_pts.append(
                                [
                                    pid,
                                    uid,
                                    xx,
                                    yy,
                                    zz,
                                    args[0],
                                    args[1],
                                    args[2],
                                    dir_idx,
                                ]
                            )

            poss_pts = sorted(
                poss_pts,
                key=lambda x: (
                    -(self.all_ulds[x[1]].capacity - (self.uld_wts)[x[1]]),
                    x[4],
                    (
                        abs(
                            min(x[2], (self.all_ulds[x[1]].length - x[2] - x[5]))
                            + min(x[3], (self.all_ulds[x[1]].width - x[3] - x[6]))
                        )
                    ),
                    (x[2] * x[2] + x[3] * x[3] + x[4] * x[4]),
                ),
            )

            if len(poss_pts) == 0:
                continue
            else:
                self.resultant_data.append(
                    [
                        poss_pts[0][0],
                        poss_pts[0][1],
                        poss_pts[0][2],
                        poss_pts[0][3],
                        poss_pts[0][4],
                        poss_pts[0][2] + poss_pts[0][5],
                        poss_pts[0][3] + poss_pts[0][6],
                        poss_pts[0][4] + poss_pts[0][7],
                    ]
                )

                self.uld_wts[poss_pts[0][1]] += pckg.weight
                x_t = poss_pts[0][2] - poss_pts[0][5] * directs[poss_pts[0][8]][0]
                y_t = poss_pts[0][3] - poss_pts[0][6] * directs[poss_pts[0][8]][1]
                z_t = poss_pts[0][4] - poss_pts[0][7] * directs[poss_pts[0][8]][2]

                # Remove the used reference points
                uld_pts[poss_pts[0][1]].remove([x_t, y_t, z_t, poss_pts[0][8]])

                # Add 3 more reference points
                self.add_point(
                    poss_pts[0][1],
                    x_t,
                    y_t,
                    z_t,
                    poss_pts[0][5],
                    poss_pts[0][6],
                    poss_pts[0][7],
                    uld_pts,
                )

    def place_leftover(self, uld_pts, order):
        """
        Places all the leftover packages in the ULDs
        """
        for it in range(len(order)):
            pid = order[it]
            pckg = self.all_pkgs[pid]
            poss_pts = []
            a = pckg.length
            b = pckg.width
            c = pckg.height
            orient = [[a, b, c], [a, c, b], [b, a, c], [b, c, a], [c, a, b], [c, b, a]]

            for num in range(len(self.all_ulds)):
                uid = self.all_ulds[num]
                for ref_pt in uld_pts[uid]:
                    xx, yy, zz, dir_idx = ref_pt[0]

                    for args in orient:
                        xx = ref_pt[0] + (args[0] * directs[dir_idx][0])
                        yy = ref_pt[1] + (args[1] * directs[dir_idx][1])
                        zz = ref_pt[2] + (args[2] * directs[dir_idx][2])
                        if xx < 0 or yy < 0 or zz < 0:
                            continue
                        if self.final_checker(
                            uid, [xx, yy, zz], [args[0], args[1], args[2]], pid
                        ):
                            poss_pts.append(
                                [
                                    pid,
                                    uid,
                                    xx,
                                    yy,
                                    zz,
                                    args[0],
                                    args[1],
                                    args[2],
                                    dir_idx,
                                ]
                            )

            poss_pts = sorted(
                poss_pts,
                key=lambda x: (
                    -(self.all_ulds[x[1]].capacity - (self.uld_wts)[x[1]]),
                    x[4],
                    (
                        abs(
                            min(x[2], (self.all_ulds[x[1]].length - x[2] - x[5]))
                            + min(x[3], (self.all_ulds[x[1]].width - x[3] - x[6]))
                        )
                    ),
                    (x[2] * x[2] + x[3] * x[3] + x[4] * x[4]),
                ),
            )

            if len(poss_pts) == 0:
                continue
            else:
                # Update the resultant data and the reference points
                self.resultant_data.append(
                    [
                        poss_pts[0][0],
                        poss_pts[0][1],
                        poss_pts[0][2],
                        poss_pts[0][3],
                        poss_pts[0][4],
                        poss_pts[0][2] + poss_pts[0][5],
                        poss_pts[0][3] + poss_pts[0][6],
                        poss_pts[0][4] + poss_pts[0][7],
                    ]
                )

                self.uld_wts[poss_pts[0][1]] += pckg.weight

                x_t = poss_pts[0][2] - poss_pts[0][5] * directs[poss_pts[0][8]][0]
                y_t = poss_pts[0][3] - poss_pts[0][6] * directs[poss_pts[0][8]][1]
                z_t = poss_pts[0][4] - poss_pts[0][7] * directs[poss_pts[0][8]][2]

                # Remove the used reference points
                uld_pts[poss_pts[0][1]].remove([x_t, y_t, z_t, poss_pts[0][8]])

                # Add 3 more reference points
                self.add_point(
                    poss_pts[0][1],
                    x_t,
                    y_t,
                    z_t,
                    poss_pts[0][5],
                    poss_pts[0][6],
                    poss_pts[0][7],
                    uld_pts,
                )

    def check_new(self, pid, uid, x, y, z, x1, y1, z1, new_res):
        """
        Checks if the new package can be placed in the ULD
        """
        if x + x1 > (self.all_ulds[uid]).length:
            return False
        if y + y1 > (self.all_ulds[uid]).width:
            return False
        if z + z1 > (self.all_ulds[uid]).height:
            return False
        for ele in new_res:
            if ele[1] == uid:
                if check_intersection_cuboids(
                    [x, y, z],
                    [x + x1, y + y1, z + z1],
                    [ele[2], ele[3], ele[4]],
                    [ele[5], ele[6], ele[7]],
                ):
                    return False

        return True

    def push_to_side_face_first(self, typ):
        """
        Pushes the packages to the side face of the ULD.
        The `ty` parameter specifies the type of pushing to be done
        """
        cpy_res = copy.copy(self.resultant_data)
        new_res = []

        if typ == 1:
            # Push the packages to the left face of the ULD
            cpy_res = sorted(cpy_res, key=lambda x: (x[2], x[3], x[4]))
            for ele in cpy_res:
                x_c = ele[2]
                y_c = ele[3]
                z_c = ele[4]
                a = ele[5] - ele[2]
                b = ele[6] - ele[3]
                c = ele[7] - ele[4]
                fct = False
                while x_c > 0:
                    x_c -= 1
                    if not self.check_new(
                        ele[0], ele[1], x_c, y_c, z_c, a, b, c, new_res
                    ):
                        new_res.append(
                            [
                                ele[0],
                                ele[1],
                                x_c + 1,
                                y_c,
                                z_c,
                                x_c + a + 1,
                                y_c + b,
                                z_c + c,
                            ]
                        )
                        fct = True
                        break
                if not fct:
                    new_res.append(
                        [ele[0], ele[1], x_c, y_c, z_c, x_c + a, y_c + b, z_c + c]
                    )

        elif typ == 2:
            # Push the packages to the right face of the ULD
            cpy_res = sorted(cpy_res, key=lambda x: (-x[2], x[3], x[4]))
            for ele in cpy_res:
                x_c = ele[2]
                y_c = ele[3]
                z_c = ele[4]
                a = ele[5] - ele[2]
                b = ele[6] - ele[3]
                c = ele[7] - ele[4]
                fct = False
                lmt = self.all_ulds[ele[1]][1]

                while x_c < lmt - 1:
                    x_c += 1
                    if not self.check_new(
                        ele[0], ele[1], x_c, y_c, z_c, a, b, c, new_res
                    ):
                        new_res.append(
                            [
                                ele[0],
                                ele[1],
                                x_c - 1,
                                y_c,
                                z_c,
                                x_c + a - 1,
                                y_c + b,
                                z_c + c,
                            ]
                        )
                        fct = True
                        break

                if not fct:
                    new_res.append(
                        [ele[0], ele[1], x_c, y_c, z_c, x_c + a, y_c + b, z_c + c]
                    )

        elif typ == 3:
            # Push the packages to the backmost face of the ULD
            cpy_res = sorted(cpy_res, key=lambda x: (x[3], x[2], x[4]))
            for ele in cpy_res:
                x_c = ele[2]
                y_c = ele[3]
                z_c = ele[4]
                a = ele[5] - ele[2]
                b = ele[6] - ele[3]
                c = ele[7] - ele[4]
                fct = False

                while y_c > 0:
                    y_c -= 1
                    if not self.check_new(
                        ele[0], ele[1], x_c, y_c, z_c, a, b, c, new_res
                    ):
                        new_res.append(
                            [
                                ele[0],
                                ele[1],
                                x_c,
                                y_c + 1,
                                z_c,
                                x_c + a,
                                y_c + b + 1,
                                z_c + c,
                            ]
                        )
                        fct = True
                        break

                if not fct:
                    new_res.append(
                        [ele[0], ele[1], x_c, y_c, z_c, x_c + a, y_c + b, z_c + c]
                    )
        else:
            # Push the packages to the frontmost face of the ULD
            cpy_res = sorted(cpy_res, key=lambda x: (-x[3], x[2], x[4]))
            for ele in cpy_res:
                x_c = ele[2]
                y_c = ele[3]
                z_c = ele[4]
                a = ele[5] - ele[2]
                b = ele[6] - ele[3]
                c = ele[7] - ele[4]
                fct = False
                lmt = self.all_ulds[ele[1]][2]

                while y_c < lmt - 1:
                    y_c += 1
                    if not self.check_new(
                        ele[0], ele[1], x_c, y_c, z_c, a, b, c, new_res
                    ):
                        new_res.append(
                            [
                                ele[0],
                                ele[1],
                                x_c,
                                y_c - 1,
                                z_c,
                                x_c + a,
                                y_c + b - 1,
                                z_c + c,
                            ]
                        )
                        fct = True
                        break
                if not fct:
                    new_res.append(
                        [ele[0], ele[1], x_c, y_c, z_c, x_c + a, y_c + b, z_c + c]
                    )

        self.resultant_data = new_res

    def place_packages(self):
        """
        Places all the packages in the ULDs with respect to the
        priority and non-priority order
        """
        uld_pts = self.reset_uld_points()
        self.place_priority(uld_pts)
        self.push_to_side_face_first(4)
        self.push_to_side_face_first(2)

        uld_pts = self.reset_uld_points()
        self.place_economy(uld_pts)
        self.push_to_side_face_first(4)
        self.push_to_side_face_first(2)

        uld_pts = self.reset_uld_points()
        not_packed = []
        for val in self.non_priority_order:
            found = False
            for item in self.resultant_data:
                if -item[1] == val:
                    found = True
            if found == False:
                not_packed.append(val)

        self.place_leftover(uld_pts, not_packed)

    def find_fitness(self):
        """
        Finds the fitness score of the configuration
        """

        if self.evaluated == False:
            self.evaluated = True
            self.decode()
            self.place_packages()
            self.prior_ct = 0
            cntns_priority = []
            for val in self.resultant_data:
                if self.all_pkgs[val[0]].priority == 1:
                    self.prior_ct += 1
                    cntns_priority.append(val[1])

            self.cnt_prior_uld = len(list(set(cntns_priority)))
            self.score = 0
            for val in self.resultant_data:
                if self.all_pkgs[val[0]].priority == 0:
                    self.score += self.all_pkgs[val[0]].cost
            self.tot = 0

            for obj in self.all_pkgs:
                self.tot += obj.cost

            score = (
                self.tot
                - self.score
                - PENALTY_COST * self.prior_ct
                + COST_PER_ULD * self.cnt_prior_uld
            )
            self.fitness_score = score
        return self.fitness_score

    def store(self, file_name):
        """
        Stores the output in a CSV file
        The fitness score is appended to the file name
        """
        if self.evaluated == False:
            self.fitness_score = self.find_fitness()
        pd.DataFrame(f"/data/${self.resultant_data}_{self.fitness_score}").to_csv(
            file_name,
            index=False,
            header=False,
        )

class GeneticSolver:
    def __init__(
        self,
        pkgs,
        ulds,
        pop_size=2,
        cnt_genes=500,
        elites=1,
        elite_crossover_prob=0.8,
    ):
        self.org_pkgs = pkgs
        self.org_ulds = ulds
        self.uld_cnt = len(ulds)
        self.pkg_cnt = len(pkgs)

        self.pop_size = pop_size
        self.cnt_genes = cnt_genes
        self.elites = elites
        self.elite_crossover_prob = elite_crossover_prob

    def crossover(self, elite, non_elite):
        """
        Performs crossover between the elite and non-elite
        The elite has a higher probability of being selected, which is given by
        the `elite_crossover_prob` parameter
        """
        offspring = Config(self.org_pkgs, self.org_ulds)
        offspring.initialize()

        for i in range(self.uld_cnt):
            if np.random.uniform(low=0.0, high=1.0) < self.elite_crossover_prob:
                offspring.enc_priority_ord[i] = elite.enc_priority_ord[i]
            else:
                offspring.enc_priority_ord[i] = non_elite.enc_priority_ord[i]

        for i in range(self.pkg_cnt):
            if np.random.uniform(low=0.0, high=1.0) < self.elite_crossover_prob:
                offspring.enc_non_priority_ord[i] = elite.enc_non_priority_ord[i]
            else:
                offspring.enc_non_priority_ord[i] = non_elite.enc_non_priority_ord[i]
        return offspring

    def run(self):
        """
        Runs the genetic algorithm to find the best configuration
        """
        population = []
        for _ in range(self.pop_size):
            cnfg = Config(
                self.org_pkgs,
                self.org_ulds,
            )
            cnfg.initialize()
            population.append(cnfg)

        population = sorted(population, key=lambda x: (x.find_fitness()))

        for gen in range(self.cnt_genes):
            new_pop = population[: self.elites]
            elite_pop = population[: self.elites]
            non_elite_pop = population[self.elites :]

            rand_elite = random.choice(elite_pop)
            rand_non_elite = random.choice(non_elite_pop)

            offspring = self.crossover(rand_elite, rand_non_elite)
            new_pop.append(offspring)

            # Perform mutation
            for _ in range(self.pop_size - 1 - self.elites):
                rand_cnfg = Config(
                    self.org_pkgs,
                    self.org_ulds,
                )
                rand_cnfg.initialize()
                new_pop.append(rand_cnfg)

            population = new_pop
            population = sorted(population, key=lambda x: (x.find_fitness()))
            if gen >= 5 and gen % 5 == 0:
                population[0].store(gen)

        return population[0].resultant_data
    