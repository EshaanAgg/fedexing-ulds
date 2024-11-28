export const getCenterCoordinates = (position: Vector, size: Vector) =>
  [
    position[0] + size[0] / 2,
    position[1] + size[1] / 2,
    position[2] + size[2] / 2,
  ] as Vector;

export const addCoordinates = (position1: Vector, position2: Vector) =>
  [
    position1[0] + position2[0],
    position1[1] + position2[1],
    position1[2] + position2[2],
  ] as Vector;

export const scaleCoordinates = (position: Vector, scale: number) =>
  [position[0] * scale, position[1] * scale, position[2] * scale] as Vector;
