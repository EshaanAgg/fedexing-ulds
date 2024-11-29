import { BrowserRouter as Router, Routes, Route } from 'react-router';

import Arena from './pages/Arena';
import DemoPages from './pages/DemoPages';
import PackageTable from './components/PackageTable';
import UploadPackingData from './pages/UploadPackingData';

export default function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<UploadPackingData />} />
        <Route path="/arena" element={<Arena />} />

        {/* Demo paths for testing the components */}
        <Route
          path="/demo/arena"
          element={
            <DemoPages>
              <Arena />
            </DemoPages>
          }
        />
        <Route
          path="/demo/ptable"
          element={
            <DemoPages>
              <PackageTable />
            </DemoPages>
          }
        />
      </Routes>
    </Router>
  );
}
