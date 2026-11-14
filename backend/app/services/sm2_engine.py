"""
SM-2 Spaced Repetition Algorithm Engine.

Implementation of the SuperMemo SM-2 algorithm by Piotr Wozniak.
This module provides the core scheduling logic for flashcard review intervals.
"""

from dataclasses import dataclass
from datetime import date, timedelta


@dataclass
class SM2State:
    """Represents the SM-2 state for a single user-flashcard pair."""
    repetition_number: int = 0
    easiness_factor: float = 2.5
    interval_days: int = 0
    next_review_date: date | None = None

    def __post_init__(self):
        if self.next_review_date is None:
            self.next_review_date = date.today()


def sm2_update(state: SM2State, quality: int) -> SM2State:
    """
    Update SM-2 state based on a quality score.

    Args:
        state: Current SM-2 state for the card.
        quality: User's response quality (0-5).
            5 - perfect response, no hesitation
            4 - correct, after some thought
            3 - correct, with significant difficulty
            2 - incorrect, but close
            1 - incorrect, vague recollection
            0 - complete blackout

    Returns:
        New SM2State with updated repetition, interval, EF, and next review date.
    """
    if not 0 <= quality <= 5:
        raise ValueError(f"Quality must be between 0 and 5, got {quality}")

    # Always update easiness factor
    new_ef = state.easiness_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
    new_ef = max(new_ef, 1.3)  # Clamp to minimum

    if quality >= 3:
        # Correct response — advance schedule
        if state.repetition_number == 0:
            new_interval = 1
        elif state.repetition_number == 1:
            new_interval = 6
        else:
            new_interval = round(state.interval_days * new_ef)

        new_rep = state.repetition_number + 1
    else:
        # Incorrect response — reset
        new_rep = 0
        new_interval = 1

    return SM2State(
        repetition_number=new_rep,
        easiness_factor=round(new_ef, 2),
        interval_days=new_interval,
        next_review_date=date.today() + timedelta(days=new_interval),
    )


def score_to_quality(score: float) -> int:
    """
    Map a float score (0.0-5.0) from AI grading to an SM-2 integer quality.

    Args:
        score: Float score from 0.0 to 5.0

    Returns:
        Integer quality from 0 to 5
    """
    return max(0, min(5, round(score)))
