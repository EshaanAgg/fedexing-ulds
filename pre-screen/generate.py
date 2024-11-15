import random
from csv import DictWriter

NUMBER_PACKAGES = 200
DIM_LIM = (20, 50)
WT_LIM = (10, 100)

if __name__ == "__main__":
    packages = []
    total_volume = 0
    total_weight = 0

    for id in range(1, NUMBER_PACKAGES + 1):
        package = {
            "id": id,
            "length": random.randint(*DIM_LIM),
            "width": random.randint(*DIM_LIM),
            "height": random.randint(*DIM_LIM),
            "weight": random.randint(*WT_LIM),
            "score": random.randint(100, 500),
        }
        packages.append(package)

        total_volume += package["length"] * package["width"] * package["height"]
        total_weight += package["weight"]

    with open("packages.csv", "w", newline="") as file:
        writer = DictWriter(file, fieldnames=packages[0].keys())
        writer.writeheader()
        writer.writerows(packages)

    print(f"Total volume: {total_volume}")
    print(f"Total weight: {total_weight}")
