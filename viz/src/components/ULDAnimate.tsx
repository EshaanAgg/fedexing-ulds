import * as THREE from 'three';
import randomColor from 'randomcolor';
import { CameraControls, Center, Edges } from '@react-three/drei';

import { BoxWithRef } from './Box';
import {
  addCoordinates,
  getCenterCoordinates,
  scaleCoordinates,
} from '../utils/3d';
import { Canvas, useFrame } from '@react-three/fiber';
import { useProcessedUlds } from '../stores/problemDataStore';
import Ground from './Ground';

interface ULDAnimateProps {
  uldIndex: number;
}

type PackageConfig = {
  color: string;
  ref: THREE.Mesh | null;
  initialPos: Vector;
  finalPos: Vector;
};

const INTIAL_OFFSET_VECTOR = [7, 0, 0] as Vector;

const ULDAnimate = (props: ULDAnimateProps) => {
  const uldData = useProcessedUlds()[props.uldIndex];
  const packageConfig = uldData.packages.map(
    (p) =>
      ({
        color: randomColor(),
        ref: null,
        initialPos: addCoordinates(
          getCenterCoordinates(p.position, p.size),
          INTIAL_OFFSET_VECTOR,
        ),
        finalPos: getCenterCoordinates(p.position, p.size),
      }) as PackageConfig,
  );

  //   useFrame((_, delta) => {
  //     packageConfig.forEach((p) => {
  //       if (p.ref) {
  //         p.ref.rotation.y += delta;
  //       }
  //     });
  //   });

  return (
    <group>
      {/* Plot the ULD */}
      <mesh position={scaleCoordinates(uldData.size, 0.5)}>
        <lineBasicMaterial transparent opacity={0.4} />
        <boxGeometry args={uldData.size} />
        <Edges visible scale={1.01} color="black" />
      </mesh>

      {/* Plot the packages */}
      {uldData.packages.map((box, index) => (
        <BoxWithRef
          key={box.id}
          id={box.id}
          center={packageConfig[index].initialPos}
          size={box.size}
          color={packageConfig[index].color}
          ref={(ref) => (packageConfig[index].ref = ref)}
        />
      ))}
    </group>
  );
};

export default function ULDAnimateWrapper(props: ULDAnimateProps) {
  return (
    <div style={{ width: '100vw', height: '100vh' }}>
      <Canvas shadows camera={{ position: [0, 5, 10], fov: 60 }}>
        <Center top>
          <ULDAnimate {...props} />
        </Center>

        <Ground />
        <CameraControls makeDefault />
        <ambientLight intensity={0.6} />
      </Canvas>
    </div>
  );
}
