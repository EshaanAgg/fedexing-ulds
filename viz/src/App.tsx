import { Canvas } from '@react-three/fiber';
import { OrbitControls, Stats } from '@react-three/drei';
import { useUIActions, useSelectedPackage } from './stores/uiStore';

import Package from './components/Package';

const App = () => {
  const { addPackages } = useUIActions();
  const selectedPackage = useSelectedPackage();

  const boxes = [
    {
      position: [0, 0, 0] as [number, number, number],
      size: [1, 2, 3] as [number, number, number],
      color: 'red',
      id: 'Box A',
    },
    {
      position: [5, 5, 5] as [number, number, number],
      size: [1, 1, 1] as [number, number, number],
      color: 'blue',
      id: 'Box B',
    },
  ];

  addPackages(boxes);

  return (
    <div style={{ width: '100vw', height: '100vh' }}>
      <p> {selectedPackage}</p>
      <Canvas shadows camera={{ position: [10, 10, 10], fov: 50 }}>
        <ambientLight intensity={0.5} />
        <spotLight position={[10, 10, 10]} angle={0.3} castShadow />
        <OrbitControls enablePan={false} enableZoom={true} />
        <axesHelper args={[5]} />
        <Stats />

        {boxes.map((box) => (
          <Package key={box.id} {...box} />
        ))}
      </Canvas>
    </div>
  );
};

export default App;
