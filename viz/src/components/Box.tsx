import { addCoordinates } from '../utils/3d';
import { Text, Edges, Billboard } from '@react-three/drei';

interface Box {
  color?: string;
  center: [number, number, number];
  size: [number, number, number];
  id: string;
  label?: string;
}

const OFFSET_VECTOR = [0.001, 0.001, 0.001] as Vector;

function Box(props: Box) {
  return (
    // Add the offset to prevent z-fighting
    <mesh position={addCoordinates(OFFSET_VECTOR, props.center)}>
      <boxGeometry args={props.size} />
      <meshStandardMaterial color={props.color} transparent opacity={0.5} />

      {/* 3D Label */}
      {props.label && (
        <Billboard>
          <Text
            position={[0, 0, 0]}
            fontSize={0.8}
            color="black"
            anchorX="center"
            anchorY="middle"
          >
            {props.label}
          </Text>
        </Billboard>
      )}

      <Edges scale={1.0} color="black" />
    </mesh>
  );
}

export default Box;
