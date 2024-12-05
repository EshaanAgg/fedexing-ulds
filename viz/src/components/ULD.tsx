import Box from './Box';
import { Billboard, Edges, Text } from '@react-three/drei';
import { addCoordinates, getCenterCoordinates } from '../utils/3d';
import { useActiveUldActions } from '../stores/activeUldStore';

interface ULDProps {
  uld: ULDMeta;
  mode: string;
}

const ULD_LABEL_OFFSET = 0.4;

export const ULD = (props: ULDProps) => {
  const uldData = props.uld;
  const { activateUld } = useActiveUldActions();

  return (
    <group onClick={() => activateUld(uldData.id)}>
      {/* Plot the ULD */}
      <mesh position={getCenterCoordinates(props.uld.position, props.uld.size)}>
        <lineBasicMaterial transparent opacity={0.4} />
        <boxGeometry args={uldData.size} />
        <Edges visible scale={1.01} color="black" />
        <Billboard>
          <Text
            fontSize={0.3}
            color="black"
            anchorX="center"
            anchorY="middle"
            position={[0, uldData.size[1] / 2 + ULD_LABEL_OFFSET, 0]}
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
          color={box.color}
          id={box.id}
          priority={box.priority}
          mode={props.mode}
        />
      ))}
    </group>
  );
};
