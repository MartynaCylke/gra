import sys
from pathlib import Path

# dodaj katalog główny (gra/) do sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
