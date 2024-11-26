import UploadPackingData from './components/UploadPackingData';
import {
  useProblemDataAvailable,
  useProcessedUlds,
} from './stores/problemDataStore';

const App = () => {
  const dataAvailable = useProblemDataAvailable();
  const processedUlds = useProcessedUlds();

  if (!dataAvailable) return <UploadPackingData />;
  return (
    <div>
      <h1>Problem Data Available</h1>
      <p>Processed ULDs: {processedUlds.length}</p>
    </div>
  );
};

export default App;
