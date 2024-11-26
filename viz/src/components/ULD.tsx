import React from 'react';
import Box from './Box';
import { addCoordinates } from '../utils/3d';
import { getRandomColor } from '../utils/three';

export const ULD: React.FC<ULDMeta> = (props: ULDMeta) => {
  return (
    <>
      {/* Plot the ULD */}
      <Box
        position={props.position}
        size={props.size}
        id={props.id}
        label={`ULD ${props.id}`}
        color="none"
      />

      {/* Plot the packages */}
      {props.packages.map((box) => (
        <Box
          key={box.id}
          position={addCoordinates(box.position, props.position)}
          size={box.size}
          color={getRandomColor()}
          id={box.id}
        />
      ))}
    </>
  );
};
