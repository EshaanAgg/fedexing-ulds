type ULDData = {
  id: string;
  length: number;
  width: number;
  height: number;
  weight: number;
};

type PackageData = {
  id: string;
  length: number;
  width: number;
  height: number;
  weight: number;
  priority: boolean;
  cost: number;
};

type PackingResult = {
  uldID: string;
  packageID: string;
  x1: number;
  y1: number;
  z1: number;
  x2: number;
  y2: number;
  z2: number;
};

type PackingRequest = {
  ulds: ULDData[];
  packages: PackageData[];
  packingResults: PackingResult[];
};

export const getPlottingData = (request: PackingRequest): ULDMeta[] => {
  const ULDs: ULDMeta[] = [];

  for (const row of request.packingResults) {
    // Fetch the target ULD and create one if it doesn't exist
    const uldData = request.ulds.find((uld) => uld.id === row.uldID);
    if (!uldData) {
      console.error(`ULD with ID ${row.uldID} not found in the request.`);
      continue;
    }

    let uldIdx = ULDs.findIndex((uld) => uld.id === row.uldID);
    if (uldIdx === -1) {
      ULDs.push({
        id: row.uldID,
        // Set the position to be origin for now
        position: [0, 0, 0],
        size: [uldData.length, uldData.width, uldData.height],
        packages: [],
        weight: uldData.weight,
      });
      uldIdx = ULDs.length - 1;
    }

    // Fetch the target package and create one in the ULD
    const packageData = request.packages.find(
      (pkg) => pkg.id === row.packageID,
    );
    if (!packageData) {
      console.error(
        `Package with ID ${row.packageID} not found in the request.`,
      );
      continue;
    }

    ULDs[uldIdx].packages.push({
      id: row.packageID,
      position: [row.x1, row.y1, row.z1],
      size: [row.x2 - row.x1, row.y2 - row.y1, row.z2 - row.z1],
      weight: packageData.weight,
      priority: packageData.priority,
      cost: packageData.cost,
    });
  }

  // Change the ULD positions to be non-overlapping
  // Z = 0 for all, and group the ULDs in multiple rows of rowItems ULD each
  const padding = 20,
    rowItems = 3;

  let lastY = 0;

  for (let i = 0; i < ULDs.length; i += rowItems) {
    let maxY = 0;

    let lastX = 0;
    for (let j = i; j < Math.min(i + rowItems, ULDs.length); j++) {
      ULDs[j].position = [lastX, lastY, 0];
      lastX += ULDs[j].size[0] + padding;
      maxY = Math.max(maxY, ULDs[j].size[1]);
    }

    lastY += maxY + padding;
  }

  return ULDs;
};
