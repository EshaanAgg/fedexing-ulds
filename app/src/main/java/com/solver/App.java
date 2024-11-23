package com.solver;

import java.util.Optional;

public class App {
    public static void main(String[] args) {
        // If a number is passed as an argument, it will be used as a limit
        // for the number of packages to load

        Optional<Integer> limit = Optional.empty();
        if (args.length > 0) {
            try {
                limit = Optional.of(Integer.parseInt(args[0]));
            } catch (NumberFormatException e) {
                System.out.println("Invalid limit. Using default limit.");
            }
        }

        PackageLoadingProblem.solveModel(limit);
    }
}
