import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from './context/AuthContext';
import Navbar from './components/Layout/Navbar';
import ProtectedRoute from './components/Layout/ProtectedRoute';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import DashboardPage from './pages/DashboardPage';
import UploadPage from './pages/UploadPage';
import FlashcardsPage from './pages/FlashcardsPage';
import QuizPage from './pages/QuizPage';
import './App.css';

function App() {
  const { user } = useAuth();

  return (
    <div className="app">
      {user && <Navbar />}
      <main className="main-content">
        <Routes>
          {/* Public routes */}
          <Route path="/login" element={user ? <Navigate to="/" /> : <LoginPage />} />
          <Route path="/register" element={user ? <Navigate to="/" /> : <RegisterPage />} />

          {/* Protected routes */}
          <Route element={<ProtectedRoute />}>
            <Route path="/" element={<DashboardPage />} />
            <Route path="/upload" element={<UploadPage />} />
            <Route path="/flashcards" element={<FlashcardsPage />} />
            <Route path="/quiz" element={<QuizPage />} />
          </Route>

          {/* Fallback */}
          <Route path="*" element={<Navigate to="/" />} />
        </Routes>
      </main>
    </div>
  );
}

export default App;
