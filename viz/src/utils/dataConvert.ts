import randomColor from 'randomcolor';
import { z } from 'zod';

export const ULDDataSchema = z.object({
  id: z.string(),
  length: z.number(),
  width: z.number(),
  height: z.number(),
  weight: z.number(),
});
export type ULDData = z.infer<typeof ULDDataSchema>;

export const PackageDataSchema = z.object({
  id: z.string(),
  length: z.number(),
  width: z.number(),
  height: z.number(),
  weight: z.number(),
  priority: z.coerce.boolean(),
  cost: z.number(),
});
export type PackageData = z.infer<typeof PackageDataSchema>;

export const PackingResultSchema = z.object({
  uld_id: z.string(),
  pack_id: z.string(),
  x1: z.number(),
  y1: z.number(),
  z1: z.number(),
  x2: z.number(),
  y2: z.number(),
  z2: z.number(),
});
export type PackingResult = z.infer<typeof PackingResultSchema>;

export type PackingRequest = {
  ulds: ULDData[];
  packages: PackageData[];
  packingResults: PackingResult[];
};

export const getProcessedULDs = (
  request: PackingRequest,
  scaleFactor: number = 1 / 100,
): ULDMeta[] => {
  const ULDs: ULDMeta[] = [];

  for (const row of request.packingResults) {
    // Fetch the target ULD and create one if it doesn't exist
    const uldData = request.ulds.find((uld) => uld.id === row.uld_id);
    if (!uldData) {
      console.error(`ULD with ID ${row.uld_id} not found in the request.`);
      continue;
    }

    let uldIdx = ULDs.findIndex((uld) => uld.id === row.uld_id);
    if (uldIdx === -1) {
      ULDs.push({
        id: row.uld_id,
        // Set the position to be origin for now
        position: [0, 0, 0],
        size: [uldData.length, uldData.width, uldData.height],
        packages: [],
        weight: uldData.weight,
      });
      uldIdx = ULDs.length - 1;
    }

    // Fetch the target package and create one in the ULD
    const packageData = request.packages.find((pkg) => pkg.id === row.pack_id);
    if (!packageData) {
      console.error(`Package with ID ${row.pack_id} not found in the request.`);
      continue;
    }

    ULDs[uldIdx].packages.push({
      id: row.pack_id,
      position: [row.x1, row.y1, row.z1],
      size: [row.x2 - row.x1, row.y2 - row.y1, row.z2 - row.z1],
      weight: packageData.weight,
      priority: packageData.priority,
      cost: packageData.cost,
      color: randomColor({ luminosity: 'light' }),
    });
  }

  ULDs.sort((a, b) => a.id.localeCompare(b.id));

  // Change the ULD positions to be non-overlapping
  // Z = 0 for all, and group the ULDs in multiple rows of rowItems ULD each
  const padding = 300,
    rowItems = 2;

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

  return scaleULDs(shiftCoordinates(ULDs), scaleFactor);
};

/**
 * Scales the ULDs by the given scale factor
 *
 * @param ULDs The ULDs to scale
 * @param scale The scale factor to apply
 * @returns The scaled ULDs
 */
export const scaleULDs = (ULDs: ULDMeta[], scale: number): ULDMeta[] => {
  return ULDs.map((uld) => ({
    ...uld,
    size: [uld.size[0] * scale, uld.size[1] * scale, uld.size[2] * scale],
    position: [
      uld.position[0] * scale,
      uld.position[1] * scale,
      uld.position[2] * scale,
    ],
    packages: uld.packages.map((pkg) => ({
      ...pkg,
      size: [pkg.size[0] * scale, pkg.size[1] * scale, pkg.size[2] * scale],
      position: [
        pkg.position[0] * scale,
        pkg.position[1] * scale,
        pkg.position[2] * scale,
      ],
    })),
  }));
};

/**
 * Shifts the coordinates of the incoming ULD data to match the three.js coordinate system.
 *
 * @param ULDs The ULDs to shift
 * @returns The shifted ULDs
 */
export const shiftCoordinates = (ULDs: ULDMeta[]): ULDMeta[] => {
  return ULDs.map((uld) => ({
    ...uld,
    size: [uld.size[0], uld.size[2], -uld.size[1]],
    position: [uld.position[0], uld.position[2], -uld.position[1]],
    packages: uld.packages.map((pkg) => ({
      ...pkg,
      size: [pkg.size[0], pkg.size[2], -pkg.size[1]],
      position: [pkg.position[0], pkg.position[2], -pkg.position[1]],
    })),
  }));
};

export const getOrientation = (orgDim: Vector, rotatedDim: Vector): string => {
  const orientations = [
    {
      label: 'XYZ',
      dims: [orgDim[0], orgDim[1], orgDim[2]],
    },
    {
      label: 'XZY',
      dims: [orgDim[0], orgDim[2], orgDim[1]],
    },
    {
      label: 'YXZ',
      dims: [orgDim[1], orgDim[0], orgDim[2]],
    },
    {
      label: 'YZX',
      dims: [orgDim[1], orgDim[2], orgDim[0]],
    },
    {
      label: 'ZXY',
      dims: [orgDim[2], orgDim[0], orgDim[1]],
    },
    {
      label: 'ZYX',
      dims: [orgDim[2], orgDim[1], orgDim[0]],
    },
  ];

  for (const orientation of orientations)
    if (
      orientation.dims[0] === rotatedDim[0] &&
      orientation.dims[1] === rotatedDim[1] &&
      orientation.dims[2] === rotatedDim[2]
    )
      return orientation.label;

  return 'Unknown Orientation';
};

export const getLoadingPlan = (
  uldID: string,
  solnData: PackingResult[],
  pkgData: PackageData[],
) => {
  const headers = ['S. No.', 'Package ID', 'R1', 'R2', 'Orientation'];
  const data: string[][] = [];

  const solRows = solnData.filter((row) => row.uld_id === uldID);
  solRows.forEach((row, index) => {
    const orgPkg = pkgData.find((pkg) => pkg.id === row.pack_id);
    if (!orgPkg)
      throw new Error(
        `Package with ID ${row.pack_id} not found in the request.`,
      );

    data.push([
      (index + 1).toString(),
      row.pack_id,
      `(${row.x1}, ${row.y1}, ${row.z1})`,
      `(${row.x2}, ${row.y2}, ${row.z2})`,
      getOrientation(
        [orgPkg.length, orgPkg.width, orgPkg.height],
        [row.x2 - row.x1, row.y2 - row.y1, row.z2 - row.z1],
      ),
    ]);
  });

  return { headers, data };
};
