import * as THREE from 'three';
import { useRef } from 'react';
import { Text } from '@mantine/core';
import { useControls, button, buttonGroup, folder } from 'leva';
import { Canvas, useFrame, useThree } from '@react-three/fiber';
import {
  Center,
  CameraControls,
  KeyboardControls,
  useKeyboardControls,
} from '@react-three/drei';

import { ULD } from './../components/ULD';
import { useProcessedUlds } from '../stores/problemDataStore';
import Ground from '../components/Ground';

const { DEG2RAD } = THREE.MathUtils;

interface SceneProps {
  uldData: ULDMeta[];
}

function Scene(props: SceneProps) {
  const cameraControlsRef = useRef<CameraControls>(null!);

  const { camera } = useThree();

  // Camera controls from the hovering menu
  const { mode } = useControls({
    mode: {
      label: 'View Mode',
      value: 'All',
      options: ['All', 'Priority', 'Economy'],
    },
    'Camera Controls': folder(
      {
        thetaGrp: buttonGroup({
          label: 'Rotate Theta',
          opts: {
            '-45º': () =>
              cameraControlsRef.current.rotate(-45 * DEG2RAD, 0, true),
            '+45º': () =>
              cameraControlsRef.current.rotate(45 * DEG2RAD, 0, true),
          },
        }),
        phiGrp: buttonGroup({
          label: 'Rotate Phi',
          opts: {
            '-20º': () =>
              cameraControlsRef.current.rotate(0, 20 * DEG2RAD, true),
            '+20º': () =>
              cameraControlsRef.current.rotate(0, -20 * DEG2RAD, true),
          },
        }),
        translateGrp: buttonGroup({
          label: 'Height',
          opts: {
            Up: () => cameraControlsRef.current.truck(0, -1, true),
            Down: () => cameraControlsRef.current.truck(0, 1, true),
          },
        }),
        zoomGrp: buttonGroup({
          label: 'Zoom',
          opts: {
            Close: () => cameraControlsRef.current.zoom(camera.zoom / 2, true),
            Far: () => cameraControlsRef.current.zoom(-camera.zoom / 2, true),
          },
        }),
        Reset: button(() => cameraControlsRef.current.reset(true)),
      },
      { collapsed: true },
    ),
  });

  // Keyboard controls for the camera
  const [, get] = useKeyboardControls();
  useFrame((_, delta) => {
    const { forward, backward, left, right } = get();
    const SPEED = 5;

    if (forward) cameraControlsRef.current.forward(SPEED * delta);
    if (backward) cameraControlsRef.current.forward(-SPEED * delta);
    if (left) cameraControlsRef.current.truck(-SPEED * delta, 0, true);
    if (right) cameraControlsRef.current.truck(SPEED * delta, 0, true);
  });

  return (
    <>
      {/* Visible Elements */}
      <group position-y={-0.5}>
        <Center top>
          <mesh>
            {props.uldData.map((uld, index) => (
              <ULD key={index} uld={uld} mode={mode} />
            ))}
          </mesh>
        </Center>

        <CameraControls enabled ref={cameraControlsRef} />
        <Ground />
        <ambientLight intensity={0.6} />
      </group>
    </>
  );
}

function Arena() {
  const uldData = useProcessedUlds();

  if (uldData.length === 0)
    return (
      <Text>No ULD data found. Please upload a CSV file with ULD data.</Text>
    );

  return (
    <div style={{ width: '100vw', height: '90vh' }}>
      <Canvas shadows camera={{ position: [0, 8, 18], fov: 60 }}>
        <KeyboardControls
          map={[
            { name: 'forward', keys: ['ArrowUp', 'w', 'W'] },
            { name: 'backward', keys: ['ArrowDown', 's', 'S'] },
            { name: 'left', keys: ['ArrowLeft', 'a', 'A'] },
            { name: 'right', keys: ['ArrowRight', 'd', 'D'] },
          ]}
        >
          <Scene uldData={uldData} />
        </KeyboardControls>
      </Canvas>
    </div>
  );
}

export default Arena;
