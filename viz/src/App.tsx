import { BrowserRouter as Router, Routes, Route } from 'react-router';

import Arena from './pages/Arena';
import UploadPackingData from './pages/UploadPackingData';
import DemoArena from './pages/DemoArena';

export default function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<UploadPackingData />} />
        <Route path="/arena" element={<Arena />} />
        <Route path="/demo-arena" element={<DemoArena />} />
      </Routes>
    </Router>
  );
}
