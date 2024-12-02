import gsap from 'gsap';
import { useRef, useState } from 'react';
import { Canvas } from '@react-three/fiber';
import { Button, Dialog, Flex, Group, Text } from '@mantine/core';
import { CameraControls, Edges } from '@react-three/drei';
import {
  addCoordinates,
  getCenterCoordinates,
  scaleCoordinates,
} from '../utils/3d';

import Ground from './Ground';
import AnimatedBox from './AnimatedBox';
import { useProcessedUlds } from '../stores/problemDataStore';
import { IconPlayerPause, IconPlayerPlay } from '@tabler/icons-react';
import { useParams } from 'react-router';

interface AnimatedULDProps {
  uldData: ULDMeta;
  timelineRef: React.MutableRefObject<gsap.core.Timeline>;
  packageConfig: PackageConfig[];
}

type PackageConfig = {
  color: string;
  initialPos: Vector;
  finalPos: Vector;
};

const INTIAL_OFFSET_VECTOR = [7, 1, -3] as Vector;

const AnimatedULD = (props: AnimatedULDProps) => {
  const uldData = props.uldData;

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
        <AnimatedBox
          key={box.id}
          size={box.size}
          initialPos={props.packageConfig[index].initialPos}
          finalPos={props.packageConfig[index].finalPos}
          color={props.packageConfig[index].color}
          label={box.id}
          delay={0.5}
          animationDuration={1}
          timeline={props.timelineRef.current}
        />
      ))}
    </group>
  );
};

export default function AnimatedULDWrapper() {
  const { uldId } = useParams<string>();

  if (!uldId)
    return <Text size="lg">No ULD ID provided. Please provide a ULD ID</Text>;

  const timelineRef = useRef(
    gsap.timeline({
      paused: true,
    }),
  );

  const uldData = useProcessedUlds().find((u) => u.id === uldId);
  if (!uldData)
    return (
      <Text size="lg">No ULD found with ID {uldId}. Please try again</Text>
    );

  const [playing, setPlaying] = useState(false);

  let lastPackagePosition = INTIAL_OFFSET_VECTOR;
  const packageConfig = uldData.packages.map((p) => {
    const config = {
      initialPos: lastPackagePosition,
      finalPos: getCenterCoordinates(p.position, p.size),
      color: p.color,
    } as PackageConfig;

    lastPackagePosition = addCoordinates(lastPackagePosition, [
      p.size[0],
      0,
      0,
    ]);

    return config;
  });

  return (
    <>
      <Dialog opened style={{ maxWidth: '180px', background: 'lightgrey' }}>
        <Group justify="center">
          <Button
            onClick={() => {
              if (playing) timelineRef.current.pause();
              else timelineRef.current.play();
              setPlaying(!playing);
            }}
          >
            <Flex justify="center" direction="row" align="center">
              {playing ? (
                <>
                  <IconPlayerPause /> <Text ml="md">Pause</Text>
                </>
              ) : (
                <>
                  <IconPlayerPlay /> <Text ml="md">Play </Text>
                </>
              )}
            </Flex>
          </Button>
        </Group>
      </Dialog>

      <div style={{ width: '100vw', height: '100vh' }}>
        <Canvas shadows camera={{ position: [0, 5, 10], fov: 60 }}>
          <AnimatedULD
            timelineRef={timelineRef}
            uldData={uldData}
            packageConfig={packageConfig}
          />

          <Ground />
          <CameraControls makeDefault />
          <ambientLight intensity={0.6} />
        </Canvas>
      </div>
    </>
  );
}
