import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import TopBar from './components/TopBar';
import Dashboard from './pages/Dashboard';
import StockManager from './pages/StockManager';
import Predictor from './pages/Predictor';
import Analytics from './pages/Analytics';
import EDA from './pages/EDA';

export default function App() {
  return (
    <BrowserRouter>
      <div className="erp-layout">
        <Sidebar />
        <div className="erp-main">
          <TopBar />
          <main className="erp-content">
            <Routes>
              <Route path="/" element={<Navigate to="/dashboard" replace />} />
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/stocks" element={<StockManager />} />
              <Route path="/predictor" element={<Predictor />} />
              <Route path="/eda" element={<EDA />} />
              <Route path="/analytics" element={<Analytics />} />
            </Routes>
          </main>
        </div>
      </div>
    </BrowserRouter>
  );
}
