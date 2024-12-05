import { addCoordinates } from '../utils/3d';
import { Text, Edges, Billboard } from '@react-three/drei';

interface Box {
  color?: string;
  center: [number, number, number];
  size: [number, number, number];
  id: string;
  label?: string;
  priority: boolean;
  mode: string;
}

const getIsVisible = (mode: string, isPriority: boolean) => {
  if (mode === 'All') {
    return true;
  } else if (mode === 'Priority') {
    return isPriority;
  } else {
    return !isPriority;
  }
};

const OFFSET_VECTOR = [0.001, 0.001, 0.001] as Vector;

function Box(props: Box) {
  return (
    // Add the offset to prevent z-fighting
    <mesh
      position={addCoordinates(OFFSET_VECTOR, props.center)}
      visible={getIsVisible(props.mode, props.priority)}
    >
      <boxGeometry args={props.size} />
      <meshStandardMaterial color={props.color} opacity={0.75} />

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

      <Edges scale={0.99} color="black" lineWidth={1} />
    </mesh>
  );
}

export default Box;
