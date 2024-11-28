import Box from './Box';
import { addCoordinates } from '../utils/3d';
import { getRandomColor } from '../utils/three';

interface ULDProps {
  uld: ULDMeta;
}

export const ULD = (props: ULDProps) => {
  const uldData = props.uld;

  return (
    <group>
      {/* Plot the ULD */}
      <Box
        position={uldData.position}
        size={uldData.size}
        id={uldData.id}
        label={`ULD ${uldData.id}`}
      />

      {/* Plot the packages */}
      {uldData.packages.map((box) => (
        <Box
          key={box.id}
          position={addCoordinates(box.position, uldData.position)}
          size={box.size}
          color={getRandomColor()}
          id={box.id}
        />
      ))}
    </group>
  );
};
