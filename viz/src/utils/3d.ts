export const getCenterCoordinates = (
  position: [number, number, number],
  size: [number, number, number],
) =>
  [
    position[0] + size[0] / 2,
    position[1] + size[1] / 2,
    position[2] + size[2] / 2,
  ] as [number, number, number];

export const addCoordinates = (
  position1: [number, number, number],
  position2: [number, number, number],
) =>
  [
    position1[0] + position2[0],
    position1[1] + position2[1],
    position1[2] + position2[2],
  ] as [number, number, number];
