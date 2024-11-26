import { Mesh } from 'three';
import React, { useRef, useState } from 'react';
import { Text, Edges } from '@react-three/drei';

import { useUIActions } from '../stores/uiStore';
import { getCenterCoordinates } from '../utils/3d';

interface Package extends PackageMeta {
  color: string;
}

const Package: React.FC<Package> = (props: Package) => {
  const meshRef = useRef<Mesh>(null);
  const [isSelected, setIsSelected] = useState(false);
  const { selectPackage, deselectPackage } = useUIActions();

  const handleClick = () => {
    setIsSelected((prev) => !prev);
    if (isSelected) selectPackage(props.id);
    else deselectPackage(props.id);
  };

  return (
    <mesh
      ref={meshRef}
      position={getCenterCoordinates(props.position, props.size)}
      castShadow
      receiveShadow
      onClick={handleClick}
    >
      <boxGeometry args={props.size} />
      <meshStandardMaterial color={props.color} transparent opacity={0.5} />

      {/* 3D Label */}
      <Text
        position={[0, 0, 0]}
        fontSize={0.1}
        color="black"
        anchorX="center"
        anchorY="middle"
      >
        Package {props.id}
      </Text>

      <Edges scale={1.01} color="black" />
    </mesh>
  );
};

export default Package;
