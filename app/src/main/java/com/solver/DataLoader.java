package com.solver;

import com.opencsv.CSVReader;

import java.io.FileReader;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;

class Package {
    public String id;
    public int length;
    public int width;
    public int height;
    public boolean priority;
    public int cost;
    public int weight;

    public int get(String dimension) {
        switch (dimension) {
            case "length":
                return length;
            case "width":
                return width;
            case "height":
                return height;
            default:
                return 0;
        }
    }
}

class ULD {
    public String id;
    public int length;
    public int width;
    public int height;
    public int capacity;

    public int get(String dimension) {
        switch (dimension) {
            case "length":
                return length;
            case "width":
                return width;
            case "height":
                return height;
            default:
                return 0;
        }
    }
}

public class DataLoader {
    private static final String DEFAULT_PACKAGE_FILE = "../data/packages.csv";
    private static final String DEFAULT_ULD_FILE = "../data/ulds.csv";

    public static List<Package> loadPackages(String filePath, Optional<Integer> limit) {
        List<Package> packages = new ArrayList<>();
        try (CSVReader reader = new CSVReader(new FileReader(filePath))) {
            String[] nextLine;
            // Skip the header row
            reader.readNext();

            int count = 0;
            while ((nextLine = reader.readNext()) != null && (!limit.isPresent() || count < limit.get())) {
                Package pack = new Package();
                pack.id = nextLine[0];
                pack.length = Integer.parseInt(nextLine[1]);
                pack.width = Integer.parseInt(nextLine[2]);
                pack.height = Integer.parseInt(nextLine[3]);
                pack.weight = Integer.parseInt(nextLine[4]);
                pack.priority = "Priority".equalsIgnoreCase(nextLine[5]);
                pack.cost = "-".equals(nextLine[6]) ? 0 : Integer.parseInt(nextLine[6]);
                packages.add(pack);
                count++;
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
        return packages;
    }

    public static List<Package> loadPackages(Optional<Integer> limit) {
        return loadPackages(DEFAULT_PACKAGE_FILE, limit);
    }

    public static List<ULD> loadULDs(String filePath) {
        List<ULD> ulds = new ArrayList<>();
        try (CSVReader reader = new CSVReader(new FileReader(filePath))) {
            String[] nextLine;
            // Skip the header row
            reader.readNext();
            while ((nextLine = reader.readNext()) != null) {
                ULD uld = new ULD();
                uld.id = nextLine[0];
                uld.length = Integer.parseInt(nextLine[1]);
                uld.width = Integer.parseInt(nextLine[2]);
                uld.height = Integer.parseInt(nextLine[3]);
                uld.capacity = Integer.parseInt(nextLine[4]);
                ulds.add(uld);
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
        return ulds;
    }

    public static List<ULD> loadULDs() {
        return loadULDs(DEFAULT_ULD_FILE);
    }
}
