import * as THREE from 'three';
import { useRef } from 'react';
import { Text } from '@mantine/core';
import { useControls, button, buttonGroup } from 'leva';
import { Canvas, useFrame, useThree } from '@react-three/fiber';
import {
  Center,
  Grid,
  CameraControls,
  KeyboardControls,
  useKeyboardControls,
} from '@react-three/drei';

import { ULD } from './../components/ULD';
import { useProcessedUlds } from '../stores/problemDataStore';

const { DEG2RAD } = THREE.MathUtils;

interface SceneProps {
  uldData: ULDMeta[];
}

function Scene(props: SceneProps) {
  const cameraControlsRef = useRef<CameraControls>(null!);

  const { camera } = useThree();

  // Grid configuration for the ground
  const gridConfig = {
    cellSize: 0.5,
    cellThickness: 0.5,
    cellColor: '#6f6f6f',
    sectionSize: 3,
    sectionThickness: 1,
    sectionColor: '#9d4b4b',
    fadeDistance: 30,
    fadeStrength: 1,
    followCamera: false,
    infiniteGrid: true,
  };

  // Camera controls from the hovering menu
  useControls(
    'General',
    {
      thetaGrp: buttonGroup({
        label: 'Rotate Theta',
        opts: {
          '-90º': () =>
            cameraControlsRef.current.rotate(-90 * DEG2RAD, 0, true),
          '-45º': () =>
            cameraControlsRef.current.rotate(-45 * DEG2RAD, 0, true),
          '+45º': () => cameraControlsRef.current.rotate(45 * DEG2RAD, 0, true),
          '+90º': () => cameraControlsRef.current.rotate(90 * DEG2RAD, 0, true),
        },
      }),
      phiGrp: buttonGroup({
        label: 'Rotate Phi',
        opts: {
          '-20º': () => cameraControlsRef.current.rotate(0, 20 * DEG2RAD, true),
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
  );

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
              <ULD key={index} uld={uld} />
            ))}
          </mesh>
        </Center>

        {/* Camera */}
        <CameraControls enabled ref={cameraControlsRef} />

        {/* Ground and lighting */}
        <Grid position={[0, -0.01, 0]} args={[10.5, 10.5]} {...gridConfig} />
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
    <div style={{ width: '100vw', height: '100vh' }}>
      <Canvas shadows camera={{ position: [0, 5, 10], fov: 60 }}>
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
