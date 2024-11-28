import Box from './Box';
import randomColor from 'randomcolor';
import { Billboard, Edges, Text } from '@react-three/drei';
import { addCoordinates, getCenterCoordinates } from '../utils/3d';

interface ULDProps {
  uld: ULDMeta;
}

export const ULD = (props: ULDProps) => {
  const uldData = props.uld;

  return (
    <group>
      {/* Plot the ULD */}
      <mesh position={getCenterCoordinates(props.uld.position, props.uld.size)}>
        <lineBasicMaterial transparent opacity={0.4} />
        <boxGeometry args={uldData.size} />
        <Edges visible scale={1.01} color="black" />
        <Billboard>
          <Text
            fontSize={0.2}
            color="black"
            anchorX="center"
            anchorY="middle"
            position={[0, 0, 0]}
          >
            {uldData.id} ({uldData.packages.length})
          </Text>
        </Billboard>
      </mesh>

      {/* Plot the packages */}
      {uldData.packages.map((box) => (
        <Box
          key={box.id}
          center={addCoordinates(
            uldData.position,
            getCenterCoordinates(box.position, box.size),
          )}
          size={box.size}
          color={randomColor()}
          id={box.id}
        />
      ))}
    </group>
  );
};
