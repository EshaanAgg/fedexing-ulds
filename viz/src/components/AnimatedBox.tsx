import { Ref, useRef } from 'react';
import { Billboard, Edges, Text } from '@react-three/drei';
import { Mesh } from 'three';
import { useGSAP } from '@gsap/react';

interface Props {
  size: Vector;
  initialPos: Vector;
  finalPos: Vector;
  color: string;
  delay: number;
  animationDuration: number;
  timeline: gsap.core.Timeline;
  label: string;
}

const Z_FIGHTING_OFFSET = 0.001;

export default function AnimatedBox(props: Props) {
  const ref: Ref<Mesh> = useRef(null!);

  useGSAP(() => {
    if (!ref.current) return;

    props.timeline.to(ref.current.position, {
      x: props.finalPos[0] + Z_FIGHTING_OFFSET,
      y: props.finalPos[1] + Z_FIGHTING_OFFSET,
      z: props.finalPos[2] + Z_FIGHTING_OFFSET,
      duration: props.animationDuration,
      delay: props.delay,
    });
  });

  return (
    <mesh position={props.initialPos} ref={ref}>
      <boxGeometry args={props.size} />
      <meshStandardMaterial color={props.color} opacity={0.75} />
      <Edges scale={0.99} color="black" />
      <Billboard>
        <Text fontSize={0.12} color="black">
          {props.label}
        </Text>
      </Billboard>
    </mesh>
  );
}
