import { Mesh } from 'three';
import { Html } from '@react-three/drei';
import React, { useRef, useState } from 'react';

import { useUIActions } from '../stores/uiStore';

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

  const centerCoordinates = [
    props.position[0] + props.size[0] / 2,
    props.position[1] + props.size[1] / 2,
    props.position[2] + props.size[2] / 2,
  ] as [number, number, number];

  return (
    <mesh
      ref={meshRef}
      position={centerCoordinates}
      castShadow
      receiveShadow
      onClick={handleClick}
    >
      <boxGeometry args={props.size} />
      <meshStandardMaterial color={props.color} transparent opacity={0.5} />

      {/* Label */}
      <Html distanceFactor={10}>
        <div
          style={{
            backgroundColor: 'white',
            padding: '2px 5px',
            borderRadius: '3px',
            fontSize: '12px',
            fontWeight: 'bold',
            transform: 'translate(-50%, -50%)',
          }}
        >
          Package {props.id}
        </div>
      </Html>
    </mesh>
  );
};

export default Package;
