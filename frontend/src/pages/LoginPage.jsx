import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

function LoginPage() {
  const { login } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await login(email, password);
    } catch (err) {
      setError(err.response?.data?.detail || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-card card">
        <div className="auth-header">
          <span style={{ fontSize: '2.5rem' }}>🧠</span>
          <h1>Welcome Back</h1>
          <p>Sign in to NoteWise AI</p>
        </div>

        {error && <div className="auth-error">{error}</div>}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Email</label>
            <input
              type="email"
              className="input"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@example.com"
              required
            />
          </div>
          <div className="form-group">
            <label>Password</label>
            <input
              type="password"
              className="input"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              required
            />
          </div>
          <button type="submit" className="btn btn-primary btn-full" disabled={loading}>
            {loading ? 'Signing in...' : 'Sign In'}
          </button>
        </form>

        <p className="auth-footer">
          Don't have an account? <Link to="/register">Sign up</Link>
        </p>
      </div>

      <style>{`
        .auth-page {
          min-height: 80vh;
          display: flex;
          align-items: center;
          justify-content: center;
          padding: 2rem;
        }
        .auth-card {
          width: 100%;
          max-width: 420px;
          padding: 2.5rem;
        }
        .auth-header {
          text-align: center;
          margin-bottom: 2rem;
        }
        .auth-header h1 {
          font-size: 1.5rem;
          margin-top: 0.75rem;
        }
        .auth-header p {
          color: var(--color-text-secondary);
          font-size: 0.875rem;
        }
        .auth-error {
          background: #fef2f2;
          color: var(--color-danger);
          padding: 0.75rem;
          border-radius: var(--radius);
          font-size: 0.875rem;
          margin-bottom: 1rem;
        }
        .form-group {
          margin-bottom: 1.25rem;
        }
        .form-group label {
          display: block;
          font-size: 0.875rem;
          font-weight: 500;
          margin-bottom: 0.375rem;
        }
        .btn-full {
          width: 100%;
          justify-content: center;
          padding: 0.75rem;
        }
        .auth-footer {
          text-align: center;
          margin-top: 1.5rem;
          font-size: 0.875rem;
          color: var(--color-text-secondary);
        }
      `}</style>
    </div>
  );
}

export default LoginPage;
