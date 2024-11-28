import { BrowserRouter as Router, Routes, Route } from 'react-router';

import Arena from './pages/Arena';
import DemoArena from './pages/DemoArena';
import UploadPackingData from './pages/UploadPackingData';

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
