import { BrowserRouter as Router, Routes, Route } from 'react-router';

import Home from './pages/Home';
import Arena from './pages/Arena';
import DemoPages from './pages/DemoPages';
import Header from './components/Header';
import DataReview from './pages/DataReview';
import DoesNotExist from './pages/DoesNotExist';
import PackageTable from './components/PackageTable';
import UploadPackingData from './pages/UploadSolutionData';
import ULDInformation from './components/ULDInformation';

export default function App() {
  return (
    <Router>
      <Header />
      <ULDInformation />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/arena" element={<Arena />} />
        <Route path="/review" element={<DataReview />} />

        {/* Demo paths for testing the components */}
        <Route path="/demo/viz" element={<UploadPackingData />} />
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

        {/* Catch all route for error pages */}
        <Route path="*" element={<DoesNotExist />} />
      </Routes>
    </Router>
  );
}
