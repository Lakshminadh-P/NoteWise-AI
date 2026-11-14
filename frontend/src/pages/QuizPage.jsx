import { useState, useEffect } from 'react';
import api from '../services/api';

function QuizPage() {
  const [quizzes, setQuizzes] = useState([]);
  const [session, setSession] = useState(null);
  const [answers, setAnswers] = useState({});
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    loadQuizzes();
  }, []);

  const loadQuizzes = async () => {
    try {
      const res = await api.get('/api/quizzes');
      setQuizzes(res.data);
    } catch (err) {
      console.error('Failed to load quizzes:', err);
    } finally {
      setLoading(false);
    }
  };

  const startQuiz = async (quizId) => {
    try {
      const res = await api.post(`/api/quizzes/${quizId}/start`);
      setSession(res.data);
      setAnswers({});
      setResults(null);
    } catch (err) {
      console.error('Failed to start quiz:', err);
    }
  };

  const submitQuiz = async () => {
    setSubmitting(true);
    try {
      const payload = {
        answers: Object.entries(answers).map(([questionId, userAnswer]) => ({
          question_id: questionId,
          user_answer: userAnswer,
        })),
      };
      const res = await api.post(`/api/quizzes/sessions/${session.session_id}/submit`, payload);
      setResults(res.data);
    } catch (err) {
      console.error('Failed to submit quiz:', err);
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) return <div className="container"><p>Loading quizzes...</p></div>;

  // Show results
  if (results) {
    return (
      <div className="container">
        <h1 style={{ marginBottom: '1.5rem' }}>✍️ Quiz Results</h1>
        <div className="card" style={{ textAlign: 'center', padding: '2rem', marginBottom: '1.5rem' }}>
          <p style={{ fontSize: '3rem', fontWeight: 700, color: 'var(--color-primary)' }}>
            {results.percentage.toFixed(0)}%
          </p>
          <p style={{ color: 'var(--color-text-secondary)' }}>
            Score: {results.total_score.toFixed(1)} / {results.total_questions * 5}
          </p>
        </div>
        {results.results.map((r, i) => (
          <div key={r.question_id} className="card" style={{ marginBottom: '1rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <strong>Q{i + 1}</strong>
              <span style={{ color: r.score >= 3 ? 'var(--color-success)' : 'var(--color-danger)', fontWeight: 600 }}>
                {r.score.toFixed(1)} / 5
              </span>
            </div>
            {r.ai_feedback && <p style={{ marginTop: '0.5rem', fontSize: '0.875rem', color: 'var(--color-text-secondary)' }}>{r.ai_feedback}</p>}
          </div>
        ))}
        <button className="btn btn-primary" onClick={() => { setSession(null); setResults(null); }}>
          Back to Quizzes
        </button>
      </div>
    );
  }

  // Show quiz in progress
  if (session) {
    return (
      <div className="container">
        <h1 style={{ marginBottom: '1.5rem' }}>✍️ {session.quiz_title}</h1>
        {session.questions.map((q, i) => (
          <div key={q.id} className="card" style={{ marginBottom: '1rem' }}>
            <p style={{ fontWeight: 600, marginBottom: '0.75rem' }}>Q{i + 1}. {q.question_text}</p>
            {q.question_type === 'mcq' && q.options ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                {Object.entries(q.options).map(([key, value]) => (
                  <label key={key} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer' }}>
                    <input
                      type="radio"
                      name={q.id}
                      value={key}
                      checked={answers[q.id] === key}
                      onChange={() => setAnswers({ ...answers, [q.id]: key })}
                    />
                    <span><strong>{key}.</strong> {value}</span>
                  </label>
                ))}
              </div>
            ) : (
              <textarea
                className="input"
                rows={3}
                placeholder="Type your answer..."
                value={answers[q.id] || ''}
                onChange={(e) => setAnswers({ ...answers, [q.id]: e.target.value })}
              />
            )}
          </div>
        ))}
        <button className="btn btn-primary" onClick={submitQuiz} disabled={submitting}>
          {submitting ? 'Grading...' : 'Submit Quiz'}
        </button>
      </div>
    );
  }

  // Show quiz list
  return (
    <div className="container">
      <h1 style={{ marginBottom: '1.5rem' }}>✍️ Quizzes</h1>
      {quizzes.length === 0 ? (
        <div className="card" style={{ textAlign: 'center', padding: '3rem' }}>
          <p style={{ fontSize: '3rem' }}>📝</p>
          <p style={{ color: 'var(--color-text-secondary)' }}>No quizzes yet. Upload a PDF to generate quizzes.</p>
        </div>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '1rem' }}>
          {quizzes.map((quiz) => (
            <div key={quiz.id} className="card">
              <h3 style={{ fontSize: '1rem', marginBottom: '0.5rem' }}>{quiz.title}</h3>
              <p style={{ fontSize: '0.8rem', color: 'var(--color-text-secondary)', marginBottom: '1rem' }}>
                {quiz.question_count} questions • {quiz.quiz_type}
              </p>
              <button className="btn btn-primary" onClick={() => startQuiz(quiz.id)}>Start Quiz</button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default QuizPage;
