import { Text, Edges, Billboard } from '@react-three/drei';

interface Box {
  color?: string;
  center: [number, number, number];
  size: [number, number, number];
  id: string;
  label?: string;
}

function Box(props: Box) {
  return (
    <mesh position={props.center}>
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
