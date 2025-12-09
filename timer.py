"""Module de mesure du temps d'exécution."""

import time
from functools import wraps


def timed(func):
    """Décorateur pour mesurer le temps d'exécution d'une fonction."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"[TIMER] {func.__name__}: {end - start:.2f} secondes")
        return result
    return wrapper


class Timer:
    """Gestionnaire de contexte pour mesurer le temps d'exécution."""

    def __init__(self, name: str = "Opération"):
        self.name = name
        self.start = None
        self.end = None

    def __enter__(self):
        self.start = time.time()
        return self

    def __exit__(self, *args):
        self.end = time.time()
        print(f"[TIMER] {self.name}: {self.elapsed:.2f} secondes")

    @property
    def elapsed(self) -> float:
        """Retourne le temps écoulé en secondes."""
        if self.end:
            return self.end - self.start
        return time.time() - self.start
