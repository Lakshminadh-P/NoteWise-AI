import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

function Navbar() {
  const { user, logout } = useAuth();
  const location = useLocation();

  const navItems = [
    { path: '/', label: 'Dashboard', icon: '📊' },
    { path: '/upload', label: 'Upload', icon: '📄' },
    { path: '/flashcards', label: 'Flashcards', icon: '🃏' },
    { path: '/quiz', label: 'Quiz', icon: '✍️' },
  ];

  return (
    <nav className="navbar">
      <div className="container navbar-inner">
        <Link to="/" className="navbar-brand">
          <span className="brand-icon">🧠</span>
          <span className="brand-text">NoteWise AI</span>
        </Link>

        <div className="nav-links">
          {navItems.map((item) => (
            <Link
              key={item.path}
              to={item.path}
              className={`nav-link ${location.pathname === item.path ? 'active' : ''}`}
            >
              <span>{item.icon}</span>
              <span>{item.label}</span>
            </Link>
          ))}
        </div>

        <div className="nav-user">
          <span className="user-name">{user?.full_name}</span>
          <button className="btn btn-outline" onClick={logout}>
            Logout
          </button>
        </div>
      </div>

      <style>{`
        .navbar {
          background: var(--color-surface);
          border-bottom: 1px solid var(--color-border);
          padding: 0.75rem 0;
          position: sticky;
          top: 0;
          z-index: 100;
        }
        .navbar-inner {
          display: flex;
          align-items: center;
          justify-content: space-between;
          gap: 1rem;
        }
        .navbar-brand {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          font-size: 1.25rem;
          font-weight: 700;
          color: var(--color-text);
        }
        .brand-icon { font-size: 1.5rem; }
        .nav-links {
          display: flex;
          gap: 0.25rem;
        }
        .nav-link {
          display: flex;
          align-items: center;
          gap: 0.375rem;
          padding: 0.5rem 0.875rem;
          border-radius: var(--radius);
          color: var(--color-text-secondary);
          font-size: 0.875rem;
          font-weight: 500;
          transition: all 0.15s ease;
        }
        .nav-link:hover { background: var(--color-bg); color: var(--color-text); }
        .nav-link.active { background: var(--color-primary); color: white; }
        .nav-user {
          display: flex;
          align-items: center;
          gap: 0.75rem;
        }
        .user-name {
          font-size: 0.875rem;
          color: var(--color-text-secondary);
        }
        @media (max-width: 768px) {
          .nav-links { display: none; }
          .user-name { display: none; }
        }
      `}</style>
    </nav>
  );
}

export default Navbar;
