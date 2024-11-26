import Arena from './components/Arena';
import UploadPackingData from './components/UploadPackingData';
import { useProblemDataAvailable } from './stores/problemDataStore';

function App() {
  const dataAvailable = useProblemDataAvailable();

  if (!dataAvailable) return <UploadPackingData />;
  return <Arena />;
}

export default App;
