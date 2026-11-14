import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import api from '../services/api';

function DashboardPage() {
  const [stats, setStats] = useState(null);
  const [schedule, setSchedule] = useState([]);
  const [mastery, setMastery] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboard();
  }, []);

  const loadDashboard = async () => {
    try {
      const [statsRes, scheduleRes, masteryRes] = await Promise.all([
        api.get('/api/dashboard/stats'),
        api.get('/api/dashboard/schedule?days=14'),
        api.get('/api/dashboard/mastery'),
      ]);
      setStats(statsRes.data);
      setSchedule(scheduleRes.data);
      setMastery(masteryRes.data);
    } catch (err) {
      console.error('Failed to load dashboard:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className="container"><p>Loading dashboard...</p></div>;

  return (
    <div className="container">
      <div className="dashboard-header">
        <h1>📊 Learning Dashboard</h1>
        <Link to="/upload" className="btn btn-primary">+ Upload PDF</Link>
      </div>

      {/* Stats Cards */}
      <div className="stats-grid">
        <div className="stat-card card">
          <div className="stat-value">{stats?.total_documents || 0}</div>
          <div className="stat-label">Documents</div>
        </div>
        <div className="stat-card card">
          <div className="stat-value">{stats?.total_flashcards || 0}</div>
          <div className="stat-label">Flashcards</div>
        </div>
        <div className="stat-card card">
          <div className="stat-value" style={{ color: 'var(--color-warning)' }}>{stats?.cards_due_today || 0}</div>
          <div className="stat-label">Due Today</div>
        </div>
        <div className="stat-card card">
          <div className="stat-value" style={{ color: 'var(--color-success)' }}>{stats?.cards_mastered || 0}</div>
          <div className="stat-label">Mastered</div>
        </div>
      </div>

      <div className="dashboard-charts">
        {/* Mastery by Topic */}
        {mastery.length > 0 && (
          <div className="card chart-card">
            <h3>Topic Mastery</h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={mastery}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="topic" tick={{ fontSize: 12 }} />
                <YAxis />
                <Tooltip />
                <Bar dataKey="mastered" fill="#10b981" name="Mastered" stackId="a" />
                <Bar dataKey="learning" fill="#6366f1" name="Learning" stackId="a" />
                <Bar dataKey="new" fill="#94a3b8" name="New" stackId="a" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}

        {/* Upcoming Reviews */}
        <div className="card chart-card">
          <h3>Upcoming Reviews</h3>
          {schedule.length === 0 ? (
            <p className="empty-state">No upcoming reviews. Upload a PDF to get started!</p>
          ) : (
            <div className="schedule-list">
              {schedule.slice(0, 10).map((item) => (
                <div key={item.flashcard_id} className="schedule-item">
                  <div className="schedule-front">{item.front}</div>
                  <div className="schedule-meta">
                    <span className="tag">{item.topic_tag || 'General'}</span>
                    <span className="date">📅 {item.next_review_date}</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      <style>{`
        .dashboard-header {
          display: flex; justify-content: space-between; align-items: center;
          margin-bottom: 1.5rem;
        }
        .dashboard-header h1 { font-size: 1.5rem; }
        .stats-grid {
          display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
          gap: 1rem; margin-bottom: 1.5rem;
        }
        .stat-card { text-align: center; }
        .stat-value { font-size: 2rem; font-weight: 700; color: var(--color-primary); }
        .stat-label { font-size: 0.875rem; color: var(--color-text-secondary); margin-top: 0.25rem; }
        .dashboard-charts {
          display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
          gap: 1.5rem;
        }
        .chart-card h3 { margin-bottom: 1rem; font-size: 1rem; }
        .empty-state { color: var(--color-text-secondary); text-align: center; padding: 2rem; }
        .schedule-list { display: flex; flex-direction: column; gap: 0.75rem; }
        .schedule-item { padding: 0.75rem; background: var(--color-bg); border-radius: var(--radius); }
        .schedule-front { font-weight: 500; margin-bottom: 0.375rem; }
        .schedule-meta { display: flex; gap: 0.75rem; font-size: 0.8rem; color: var(--color-text-secondary); }
        .tag {
          background: var(--color-primary-light); color: white;
          padding: 0.125rem 0.5rem; border-radius: 999px; font-size: 0.75rem;
        }
      `}</style>
    </div>
  );
}

export default DashboardPage;
