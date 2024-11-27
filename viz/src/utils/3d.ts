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

/**
 * Get the camera vectors for a given ULD index. The function only supports
 * ULDs in a 2x3 grid configuration. The camera vectors are ordered as [lookAt, lookFrom].
 * The lookAt vector is the position the camera is looking at, while the lookFrom vector is
 * the position of the camera.
 * The first three ULDs are viewed from the front, while the last three ULDs are viewed from the back.
 *
 * @param uldIndex The index of the ULD
 * @param position The position of the ULD
 * @param size The size of the ULD
 */
export const getCameraVectors = (
  uldIndex: number,
  position: Vector,
  size: Vector,
  d: number = 6,
): [Vector, Vector] => {
  if (uldIndex < 0 || uldIndex > 5) {
    throw new Error('ULD index must be between 0 and 5.');
  }

  const center = getCenterCoordinates(position, size);
  if (uldIndex < 3) return [center, addCoordinates(center, [0, 0, d])];

  return [center, addCoordinates(center, [0, 0, -d])];
};
