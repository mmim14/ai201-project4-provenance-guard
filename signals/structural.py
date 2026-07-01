"""Structural signal: local stylometric heuristics (no external API).

Computes three stylometric metrics and maps them to an AI-likelihood score in
[0.0, 1.0], where 0.0 = human-like and 1.0 = AI-like, following the heuristics
in planning.md ("Signals"):

  * Type-token ratio (vocabulary diversity) - AI text tends to be MORE diverse.
  * Punctuation density                     - AI text tends to use MORE punctuation.
  * Sentence-length variation               - AI text tends to be MORE uniform
                                              (lower variation) than human text.

The normalization constants below are heuristic and tunable. Stylometry is also
length-sensitive: very short inputs yield less reliable scores.
"""

import re
import statistics
import string

# Tunable normalization constants (see module docstring).
PUNCT_DENSITY_AT_MAX = 0.25  # punctuation marks per word that maps to a 1.0 AI-score
CV_AT_HUMAN = 1.0            # sentence-length coefficient-of-variation treated as fully human

# Inputs shorter than this are too small for reliable stylometry, so we return
# a neutral (maximally uncertain) score instead of a misleading one.
MIN_SENTENCES = 2
NEUTRAL_SCORE = 0.5

_WORD_RE = re.compile(r"[a-zA-Z']+")
_SENT_SPLIT_RE = re.compile(r"[.!?]+")


def _words(text: str) -> list[str]:
    return _WORD_RE.findall(text.lower())


def _sentences(text: str) -> list[str]:
    return [s for s in (p.strip() for p in _SENT_SPLIT_RE.split(text)) if s]


def _type_token_ratio(words: list[str]) -> float:
    """Unique words / total words. Higher = more diverse vocabulary."""
    if not words:
        return 0.0
    return len(set(words)) / len(words)


def _punctuation_density(text: str, word_count: int) -> float:
    """Punctuation marks per word."""
    if word_count == 0:
        return 0.0
    punct = sum(1 for ch in text if ch in string.punctuation)
    return punct / word_count


def _sentence_length_cv(sentences: list[str]) -> float:
    """Coefficient of variation (std / mean) of sentence lengths, in words.

    Higher = more variation (human-like); lower = more uniform (AI-like).
    """
    lengths = [n for n in (len(_words(s)) for s in sentences) if n > 0]
    if len(lengths) < 2:
        return 0.0
    mean = statistics.mean(lengths)
    if mean == 0:
        return 0.0
    return statistics.pstdev(lengths) / mean


def _clamp01(x: float) -> float:
    return max(0.0, min(1.0, x))


def analyze_structural(text: str) -> float:
    """Return an AI-likelihood score in [0.0, 1.0] from stylometric heuristics.

    0.0 = human-like, 1.0 = AI-like.
    """
    words = _words(text)
    sentences = _sentences(text)

    # Too short for reliable stylometry -> stay neutral (uncertain).
    if len(sentences) < MIN_SENTENCES:
        return NEUTRAL_SCORE

    ttr = _type_token_ratio(words)
    punct_density = _punctuation_density(text, len(words))
    cv = _sentence_length_cv(sentences)

    # Map each metric to an AI-likelihood component in [0.0, 1.0].
    ttr_component = _clamp01(ttr)                                     # more diverse -> more AI
    punct_component = _clamp01(punct_density / PUNCT_DENSITY_AT_MAX)  # more punctuation -> more AI
    uniformity_component = _clamp01(1.0 - cv / CV_AT_HUMAN)           # less variation -> more AI

    # Equal-weight the three heuristics.
    return (ttr_component + punct_component + uniformity_component) / 3.0
