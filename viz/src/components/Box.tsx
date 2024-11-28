import { Text, Edges, Billboard } from '@react-three/drei';
import { getCenterCoordinates } from '../utils/3d';

interface Box {
  color?: string;
  position: [number, number, number];
  size: [number, number, number];
  id: string;
  label?: string;
}

function Box(props: Box) {
  return (
    <mesh position={getCenterCoordinates(props.position, props.size)}>
      <boxGeometry args={props.size} />
      <meshStandardMaterial color={props.color} transparent opacity={0.5} />

      {/* 3D Label */}
      {props.label && (
        <Billboard>
          <Text
            position={[0, 0, 0]}
            fontSize={0.4}
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
