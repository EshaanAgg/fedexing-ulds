import { Text, Edges } from '@react-three/drei';
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
    <mesh
      position={getCenterCoordinates(props.position, props.size)}
      castShadow
      receiveShadow
    >
      <boxGeometry args={props.size} />
      <meshStandardMaterial color={props.color} transparent opacity={0.5} />

      {/* 3D Label */}
      {props.label && (
        <Text
          position={[0, 0, 0]}
          fontSize={0.1}
          color="black"
          anchorX="center"
          anchorY="middle"
        >
          {props.label}
        </Text>
      )}

      <Edges scale={1.01} color="black" />
    </mesh>
  );
}

export default Box;
