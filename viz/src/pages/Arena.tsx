import * as THREE from 'three';
import { Text } from '@mantine/core';
import { useRef } from 'react';
import { Canvas, useThree } from '@react-three/fiber';
import { Center, Grid, CameraControls } from '@react-three/drei';
import { useControls, button, buttonGroup, folder } from 'leva';

import { ULD } from './../components/ULD';
import { useProcessedUlds } from '../stores/problemDataStore';
import { getCameraVectors } from '../utils/3d';

const { DEG2RAD } = THREE.MathUtils;

<div style={{ width: '100vw', height: '100vh' }}></div>;

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

  // Folder group to control the camera movement to the ULDs
  const cameraFolderItems = props.uldData.map((uld, index) => {
    const [lookAt, lookFrom] = getCameraVectors(index, uld.position, uld.size);
    return button(() =>
      cameraControlsRef.current.setLookAt(...lookFrom, ...lookAt, true),
    );
  });

  // Camera controls from the hovering menu
  useControls({
    thetaGrp: buttonGroup({
      label: 'Rotate Theta',
      opts: {
        '-90º': () => cameraControlsRef.current.rotate(-90 * DEG2RAD, 0, true),
        '-45º': () => cameraControlsRef.current.rotate(-45 * DEG2RAD, 0, true),
        '+45º': () => cameraControlsRef.current.rotate(45 * DEG2RAD, 0, true),
        '+90º': () => cameraControlsRef.current.rotate(90 * DEG2RAD, 0, true),
      },
    }),
    phiGrp: buttonGroup({
      label: 'Rotate Phi',
      opts: {
        '-20º': () => cameraControlsRef.current.rotate(0, 20 * DEG2RAD, true),
        '+20º': () => cameraControlsRef.current.rotate(0, -20 * DEG2RAD, true),
      },
    }),
    zoomGrp: buttonGroup({
      label: 'Zoom',
      opts: {
        Close: () => cameraControlsRef.current.zoom(camera.zoom / 2, true),
        Far: () => cameraControlsRef.current.zoom(-camera.zoom / 2, true),
      },
    }),
    "ULD's": folder(
      {
        ...cameraFolderItems.reduce(
          (acc, item, index) => ({ ...acc, [`ULD ${index + 1}`]: item }),
          {},
        ),
      },
      { collapsed: true },
    ),
    Reset: button(() => cameraControlsRef.current.reset(true)),
  });

  return (
    <>
      <group position-y={-0.5}>
        <Center top>
          <mesh>
            {props.uldData.map((uld, index) => (
              <ULD key={index} {...uld} />
            ))}
          </mesh>
        </Center>
        {/* Ground */}
        <Grid position={[0, -0.01, 0]} args={[10.5, 10.5]} {...gridConfig} />
        <CameraControls enabled ref={cameraControlsRef} />
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
        <Scene uldData={uldData} />
      </Canvas>
    </div>
  );
}

export default Arena;
