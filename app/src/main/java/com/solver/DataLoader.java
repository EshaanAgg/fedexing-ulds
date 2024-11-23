package com.solver;

import java.util.List;

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
}

public class DataLoader {
    public static List<Package> loadPackages() {
        return null;
    }

    public static List<ULD> loadULDs() {
        return null;
    }
}
