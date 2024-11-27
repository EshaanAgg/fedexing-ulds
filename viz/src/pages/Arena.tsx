import { Canvas } from '@react-three/fiber';
import { CameraControls } from '@react-three/drei';
import { Text } from '@mantine/core';

import { ULD } from './../components/ULD';
import Ground from './../components/Ground';
import { useProcessedUlds } from '../stores/problemDataStore';

const MAX_DISTANCE = 700;
const MIN_DISTANCE = 50;

function Arena() {
  const uldData = useProcessedUlds();

  if (uldData.length === 0)
    return (
      <Text>No ULD data found. Please upload a CSV file with ULD data.</Text>
    );

  return (
    <div style={{ width: '100vw', height: '100vh' }}>
      <Canvas
        shadows
        camera={{
          position: [MAX_DISTANCE, MAX_DISTANCE, MAX_DISTANCE],
          far: MAX_DISTANCE * 6,
        }}
      >
        <ambientLight intensity={0.5} />
        <spotLight
          position={[MAX_DISTANCE, MAX_DISTANCE, MAX_DISTANCE]}
          angle={0.3}
          castShadow
        />

        <CameraControls minDistance={MIN_DISTANCE} enabled />
        <Ground position={[0, -0.01, 0]} args={[10.5, 10.5]} />

        {/* Plot all the ULDs */}
        {uldData.map((uld) => (
          <ULD key={uld.id} {...uld} />
        ))}
      </Canvas>
    </div>
  );
}

export default Arena;
