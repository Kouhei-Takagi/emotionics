# src/emotionics/__init__.py
from .core import activate, estimate, gyo, en, lend_ears, wave
from .matrix import gyo_matrix

__all__ = ["activate", "estimate", "gyo", "en", "lend_ears", "gyo_matrix", "wave"]
__version__ = "0.9.0"