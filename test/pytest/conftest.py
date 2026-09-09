import sys
from pathlib import Path

# bot.py runs with arsene_wenger/ on sys.path; tests need the same
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "arsene_wenger"))
