import copy
import pandas as pd


class PackageManager:
    """
    A class to manage package loading, collision checks, and dependency graph construction for ULDs
    """

    def __init__(self, num_of_total_pkgs, num_of_ulds, uld_order, lis_u, sol):
        self.num_of_total_pkgs = num_of_total_pkgs
        self.num_of_ulds = num_of_ulds
        self.uld_order = uld_order
        self.lis_u = lis_u
        self.sol = sol

        # Initialize supporting structures
        self.adj_lis = [[] for _ in range(num_of_total_pkgs)]
        self.available = [False] * num_of_total_pkgs
        self.find_pack = [[False, -1] for _ in range(num_of_total_pkgs)]
        self.uld_wise = [[] for _ in range(num_of_ulds)]
        self.package_wise_data = [[] for _ in range(num_of_total_pkgs)]
        self.in_deg = [0] * num_of_total_pkgs
        self.visited = [False] * num_of_total_pkgs
        self.final_order = []

        self.group_packages_by_uld()

    def group_packages_by_uld(self):
        """
        Groups the packages by their assigned ULDs
        """

        for item in self.sol:
            self.uld_wise[item[1]].append(item)
            self.package_wise_data[item[0]] = item
            self.find_pack[item[0]] = [True, item[1]]

    def check_new(self, uid, x, y, z, x1, y1, z1, new_res):
        """
        Check if a package can be placed in the current position without violating constraints.
        """
        # Check against ULD capacity
        if (
            x + x1 > self.lis_u[uid][1]
            or y + y1 > self.lis_u[uid][2]
            or z + z1 > self.lis_u[uid][3]
        ):
            return False

        # Check for intersection with existing packages
        for ele in new_res:
            if ele[1] == uid and self.check_intersection_cuboids(
                [x, y, z],
                [x + x1, y + y1, z + z1],
                [ele[2], ele[3], ele[4]],
                [ele[5], ele[6], ele[7]],
            ):
                return False

        return True

    def check_intersection_cuboids(
        self, cuboid1_min, cuboid1_max, cuboid2_min, cuboid2_max
    ):
        """
        Check if two cuboids intersect.
        """

        for i in range(3):
            if cuboid1_max[i] <= cuboid2_min[i] or cuboid2_max[i] <= cuboid1_min[i]:
                return False
        return True

    def push_in_z(self):
        """
        Adjust the z-coordinate of packages to minimize space wastage.
        """
        cpy_res = sorted(copy.deepcopy(self.sol), key=lambda x: (x[4], x[3], x[2]))
        new_res = []

        for ele in cpy_res:
            x_c, y_c, z_c = ele[2], ele[3], ele[4]
            a, b, c = ele[5] - x_c, ele[6] - y_c, ele[7] - z_c
            moved = False

            while z_c > 0:
                z_c -= 1
                if not self.check_new(ele[0], ele[1], x_c, y_c, z_c, a, b, c, new_res):
                    new_res.append(
                        [
                            ele[0],
                            ele[1],
                            x_c,
                            y_c,
                            z_c + 1,
                            x_c + a,
                            y_c + b,
                            z_c + c + 1,
                        ]
                    )
                    moved = True
                    break

            if not moved:
                new_res.append(
                    [ele[0], ele[1], x_c, y_c, z_c, x_c + a, y_c + b, z_c + c]
                )

        return new_res

    def find_dependencies(self, cord, dims, pid, uid, axis):
        """
        Find packages that are dependent on the current package, and initialize the dependency graph
        for the topology sort.
        """
        dependencies = []
        idx = 0 if axis == "x" else 2

        while cord[idx] > 0:
            cord[idx] -= 1
            for ele in self.uld_wise[uid]:
                if ele[0] != pid and self.check_intersection_cuboids(
                    cord,
                    [cord[i] + dims[i] for i in range(3)],
                    [ele[2], ele[3], ele[4]],
                    [ele[5], ele[6], ele[7]],
                ):
                    dependencies.append(ele[0])

        return list(dict.fromkeys(dependencies))

    def construct_graph(self, pid, uid):
        """
        Construct a dependency graph for the packages.
        """
        self.available[pid] = True
        data = next((i for i in self.uld_wise[uid] if i[0] == pid), None)

        if not data:
            return

        x, y, z = data[2:5]
        a, b, c = data[5] - x, data[6] - y, data[7] - z
        point = [x, y, z]

        dependencies = self.find_dependencies(point[:], [a, b, c], pid, uid, "x")
        dependencies += self.find_dependencies(point[:], [a, b, c], pid, uid, "z")
        dependencies = list(set(dependencies))

        self.adj_lis[pid] = dependencies
        for dep in dependencies:
            if not self.available[dep]:
                self.construct_graph(dep, uid)

    def topo_sort(self):
        """
        Perform topological sort on the dependency graph.
        """

        def dfs(pid):
            self.visited[pid] = True
            for dep in self.adj_lis[pid]:
                if not self.visited[dep]:
                    dfs(dep)
            self.final_order.append(pid)

        pkg_ind = sorted(range(self.num_of_total_pkgs), key=lambda x: self.in_deg[x])

        for pid in pkg_ind:
            if not self.visited[pid] and self.find_pack[pid][0]:
                self.construct_graph(pid, self.find_pack[pid][1])

        for pid in pkg_ind:
            if not self.visited[pid]:
                dfs(pid)

    def get_results(self):
        """
        Get the final sorted packages.
        """
        self.topo_sort()
        return self.final_order

    def export_results(self, filename="output.csv"):
        """
        Export the final sorted packages to a CSV file.
        """
        final_data = [["uld_id", "pack_id", "x1", "y1", "z1", "x2", "y2", "z2"]]

        for pid in self.final_order:
            package = self.package_wise_data[pid]
            package[0] += 1
            package[1] += 1
            final_data.append(
                ["U" + str(package[1]), "P-" + str(package[0])] + package[2:]
            )

        return pd.DataFrame(final_data).to_dict(orient="records")
