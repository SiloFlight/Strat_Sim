# tests/conftest.py
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
TESTS_ROOT = PROJECT_ROOT / "tests"

sys.path.insert(0, str(TESTS_ROOT))