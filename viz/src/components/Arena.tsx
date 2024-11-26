import { Canvas } from '@react-three/fiber';
import { OrbitControls } from '@react-three/drei';
import { useProcessedUlds } from '../stores/problemDataStore';
import { ULD } from './ULD';

const MAX_DISTANCE = 700;

function Arena() {
  const uldData = useProcessedUlds();

  if (uldData.length === 0) return null;

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
        <OrbitControls
          enablePan={true}
          enableZoom={true}
          enableRotate={true}
          maxPolarAngle={Math.PI}
          minPolarAngle={0}
        />

        {/* Plot all the ULDs */}
        {uldData.map((uld) => (
          <ULD key={uld.id} {...uld} />
        ))}
      </Canvas>
    </div>
  );
}

export default Arena;
