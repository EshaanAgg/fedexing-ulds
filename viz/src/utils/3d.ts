export const getCenterCoordinates = (
  position: [number, number, number],
  size: [number, number, number],
) =>
  [
    position[0] + size[0] / 2,
    position[1] + size[1] / 2,
    position[2] + size[2] / 2,
  ] as [number, number, number];
