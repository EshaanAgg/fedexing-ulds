import { BrowserRouter as Router, Routes, Route } from 'react-router';

import Arena from './pages/Arena';
import DemoPages from './pages/DemoPages';
import Header from './components/Header';
import DataReview from './pages/DataReview';
import PackageTable from './components/PackageTable';
import UploadPackingData from './pages/UploadPackingData';

export default function App() {
  return (
    <Router>
      <Header />
      <Routes>
        <Route path="/" element={<UploadPackingData />} />
        <Route path="/arena" element={<Arena />} />
        <Route path="/review" element={<DataReview />} />

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
