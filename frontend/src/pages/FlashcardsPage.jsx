import { useState, useEffect } from 'react';
import api from '../services/api';

function FlashcardsPage() {
  const [dueCards, setDueCards] = useState([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [flipped, setFlipped] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDueCards();
  }, []);

  const loadDueCards = async () => {
    try {
      const res = await api.get('/api/flashcards/due');
      setDueCards(res.data);
    } catch (err) {
      console.error('Failed to load flashcards:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleReview = async (quality) => {
    const card = dueCards[currentIndex];
    try {
      await api.post(`/api/flashcards/${card.id}/review`, { quality });
      setFlipped(false);
      if (currentIndex < dueCards.length - 1) {
        setCurrentIndex(currentIndex + 1);
      } else {
        setDueCards([]);
        setCurrentIndex(0);
      }
    } catch (err) {
      console.error('Failed to submit review:', err);
    }
  };

  if (loading) return <div className="container"><p>Loading flashcards...</p></div>;

  const card = dueCards[currentIndex];

  return (
    <div className="container">
      <h1 style={{ marginBottom: '1.5rem' }}>🃏 Flashcard Review</h1>

      {dueCards.length === 0 ? (
        <div className="card" style={{ textAlign: 'center', padding: '3rem' }}>
          <p style={{ fontSize: '3rem' }}>🎉</p>
          <h2>All caught up!</h2>
          <p style={{ color: 'var(--color-text-secondary)' }}>No cards due for review. Check back later.</p>
        </div>
      ) : (
        <>
          <p style={{ marginBottom: '1rem', color: 'var(--color-text-secondary)' }}>
            Card {currentIndex + 1} of {dueCards.length}
            {card.topic_tag && <span className="tag" style={{ marginLeft: '0.5rem' }}>{card.topic_tag}</span>}
          </p>

          <div className="flashcard-container" onClick={() => setFlipped(!flipped)}>
            <div className={`flashcard ${flipped ? 'flipped' : ''}`}>
              <div className="flashcard-front card">
                <p className="flashcard-label">Question</p>
                <p className="flashcard-text">{card.front}</p>
                <p className="flashcard-hint">Click to flip</p>
              </div>
              <div className="flashcard-back card">
                <p className="flashcard-label">Answer</p>
                <p className="flashcard-text">{card.back}</p>
              </div>
            </div>
          </div>

          {flipped && (
            <div className="review-buttons">
              <p style={{ marginBottom: '0.75rem', fontWeight: 500 }}>How well did you know this?</p>
              <div className="btn-row">
                <button className="btn review-btn" style={{ background: '#ef4444', color: 'white' }} onClick={() => handleReview(0)}>0 — Blackout</button>
                <button className="btn review-btn" style={{ background: '#f97316', color: 'white' }} onClick={() => handleReview(1)}>1 — Wrong</button>
                <button className="btn review-btn" style={{ background: '#f59e0b', color: 'white' }} onClick={() => handleReview(2)}>2 — Close</button>
                <button className="btn review-btn" style={{ background: '#84cc16', color: 'white' }} onClick={() => handleReview(3)}>3 — Hard</button>
                <button className="btn review-btn" style={{ background: '#22c55e', color: 'white' }} onClick={() => handleReview(4)}>4 — Good</button>
                <button className="btn review-btn" style={{ background: '#10b981', color: 'white' }} onClick={() => handleReview(5)}>5 — Perfect</button>
              </div>
            </div>
          )}
        </>
      )}

      <style>{`
        .flashcard-container { perspective: 1000px; cursor: pointer; margin-bottom: 1.5rem; }
        .flashcard {
          position: relative; width: 100%; min-height: 250px;
          transition: transform 0.6s; transform-style: preserve-3d;
        }
        .flashcard.flipped { transform: rotateY(180deg); }
        .flashcard-front, .flashcard-back {
          position: absolute; width: 100%; min-height: 250px;
          backface-visibility: hidden; display: flex;
          flex-direction: column; align-items: center; justify-content: center;
          padding: 2rem; text-align: center;
        }
        .flashcard-back { transform: rotateY(180deg); background: #f0fdf4; }
        .flashcard-label { font-size: 0.75rem; text-transform: uppercase; color: var(--color-text-secondary); margin-bottom: 1rem; letter-spacing: 0.05em; }
        .flashcard-text { font-size: 1.25rem; font-weight: 500; }
        .flashcard-hint { font-size: 0.8rem; color: var(--color-text-secondary); margin-top: 1.5rem; }
        .review-buttons { text-align: center; }
        .btn-row { display: flex; flex-wrap: wrap; gap: 0.5rem; justify-content: center; }
        .review-btn { font-size: 0.8rem; padding: 0.5rem 1rem; }
        .tag {
          background: var(--color-primary-light); color: white;
          padding: 0.125rem 0.5rem; border-radius: 999px; font-size: 0.75rem;
        }
      `}</style>
    </div>
  );
}

export default FlashcardsPage;
