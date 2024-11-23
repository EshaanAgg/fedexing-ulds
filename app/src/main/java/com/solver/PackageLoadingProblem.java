package com.solver;

import org.chocosolver.solver.Model;
import org.chocosolver.solver.Solver;
import org.chocosolver.solver.variables.IntVar;
import org.chocosolver.solver.variables.BoolVar;

import java.io.FileWriter;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

public class PackageLoadingProblem {
    final static String DEFAULT_RAW_RESULT_PATH = "../data/raw_java_choco.csv";

    public static void solveModel() {
        List<Package> packages = DataLoader.loadPackages();
        List<ULD> ulds = DataLoader.loadULDs();

        int countUld = ulds.size();
        int countPackages = packages.size();

        // Calculate BIG_M
        int maxLength = ulds.stream().mapToInt(uld -> (int) uld.length).max().orElse(0);
        int maxWidth = ulds.stream().mapToInt(uld -> (int) uld.width).max().orElse(0);
        int maxHeight = ulds.stream().mapToInt(uld -> (int) uld.height).max().orElse(0);
        int BIG_M = maxLength + maxWidth + maxHeight;

        // Create model
        Model model = new Model("Package Loading Problem");
        String[] dims = { "length", "width", "height" };

        // x[i][j] = 1 if package i is loaded into ULD j, 0 otherwise
        // start[i][j][d] is the starting position of package i in ULD j along dimension
        // d
        BoolVar[][] x = new BoolVar[countPackages][countUld];
        IntVar[][][] start = new IntVar[countPackages][countUld][dims.length];

        // Initialize variables
        for (int i = 0; i < countPackages; i++) {
            for (int j = 0; j < countUld; j++) {
                x[i][j] = model.boolVar("x_" + i + "_" + j);
                for (int d = 0; d < dims.length; d++) {
                    start[i][j][d] = model.intVar("start_" + i + "_" + j + "_" + d, 0, BIG_M);
                }
            }
        }

        for (int i = 0; i < countPackages; i++) {
            boolean priority = (boolean) packages.get(i).priority;
            if (priority) {
                // Priority constraint: Each package must be loaded in one ULD
                model.sum(x[i], "=", 1).post();
            } else {
                // Non-priority constraint: Each package must be loaded into at most 1 ULD
                model.sum(x[i], "<=", 1).post();
            }
        }

        // Intersecton constraint: Packages must not overlap in ULDs
        for (int j = 0; j < countUld; j++) {
            for (int i1 = 0; i1 < countPackages; i1++) {
                for (int i2 = i1 + 1; i2 < countPackages; i2++) {
                    BoolVar[] intersect = new BoolVar[3];

                    for (int d = 0; d < dims.length; d++) {
                        // x1 < x2 AND x1 + l1 > x2
                        BoolVar b1 = start[i1][j][d]
                                .lt(start[i2][j][d])
                                .and(
                                        start[i1][j][d]
                                                .add(packages.get(i1).get(dims[d]))
                                                .gt(start[i2][j][d]))
                                .boolVar();

                        // x2 < x1 AND x2 + l2 > x1
                        BoolVar b2 = start[i2][j][d]
                                .lt(start[i1][j][d])
                                .and(
                                        start[i2][j][d]
                                                .add(packages.get(i2).get(dims[d]))
                                                .gt(start[i1][j][d]))
                                .boolVar();

                        intersect[d] = b1.or(b2).boolVar();
                    }

                    x[i1][j]
                            .and(x[i2][j])
                            .imp(
                                    intersect[0]
                                            .and(intersect[1], intersect[2])
                                            .not())
                            .post();
                }
            }
        }

        // Weight constraint: Total weight of packages in each ULD must not exceed ULD
        // capacity
        for (int j = 0; j < countUld; j++) {
            List<IntVar> vars = new ArrayList<>();

            for (int i = 0; i < countPackages; i++) {
                IntVar w = x[i][j].mul(packages.get(i).weight).intVar();
                vars.add(w);
            }

            int uldCapacity = (int) ulds.get(j).capacity;
            model.sum(vars.toArray(new IntVar[0]), "<=", uldCapacity).post();
        }

        // Objective: Maximize shipped package costs
        List<IntVar> totalScore = new ArrayList<>();
        for (int i = 0; i < countPackages; i++) {
            for (int j = 0; j < countUld; j++) {
                totalScore.add(x[i][j].mul(packages.get(i).cost).intVar());
            }
        }

        IntVar finalScore = model.intVar("total_cost", 0, Integer.MAX_VALUE - 1);
        model.sum(totalScore.toArray(new IntVar[0]), "=", finalScore).post();

        model.setObjective(Model.MAXIMIZE, finalScore);
        Solver solver = model.getSolver();

        if (solver.solve()) {
            System.out.println("Solution found!");
            exportSolutionToCSV(x, start, countPackages, countUld, dims, DEFAULT_RAW_RESULT_PATH);
        } else {
            System.out.println("No solution found");
        }
    }

    private static void exportSolutionToCSV(BoolVar[][] x, IntVar[][][] start, int countPackages, int countUld,
            String[] dims, String filePath) {
        try (FileWriter writer = new FileWriter(filePath)) {
            writer.write("package_idx,ukd_idx,x,y,z\n");
            for (int i = 0; i < countPackages; i++) {
                for (int j = 0; j < countUld; j++) {
                    if (x[i][j].getValue() == 1) { // Check if package i is in ULD j
                        int xStart = start[i][j][0].getValue();
                        int yStart = start[i][j][1].getValue();
                        int zStart = start[i][j][2].getValue();
                        writer.write(i + "," + j + "," + xStart + "," + yStart + "," + zStart + "\n");
                    }
                }
            }
            System.out.println("Solution written to: " + filePath);
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}
