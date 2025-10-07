# smoothing.py
from collections import deque, Counter
from typing import Optional


class MajoritySmoother:
    def __init__(self, window: int = 7, min_votes: Optional[int] = None):
        """
        Majority vote smoother to stabilize noisy predictions.

        Args:
            window (int): Number of past predictions to consider.
            min_votes (Optional[int]): Minimum votes needed for a label to be emitted.
                                       If None, defaults to max(3, window//2 + 1).
        """
        self.window = window
        self.min_votes = min_votes if min_votes is not None else max(3, window // 2 + 1)
        self.buf = deque(maxlen=window)

    def push(self, label: Optional[str]) -> Optional[str]:
        """
        Push a new label into the buffer and return the smoothed result.

        Args:
            label (Optional[str]): New prediction (or None for no detection).

        Returns:
            Optional[str]: Smoothed prediction, or None if no dominant label yet.
        """
        self.buf.append(label)

        if len(self.buf) < self.window:
            return None

        vals = [v for v in self.buf if v is not None]
        if not vals:
            return None

        top, cnt = Counter(vals).most_common(1)[0]

        if cnt >= self.min_votes:
            return top
        return None

    def clear(self):
        """Reset the buffer."""
        self.buf.clear()
