import sys
from pathlib import Path

projectRoot = Path(__file__).parent
sys.path.insert(0, str(projectRoot))

from app.appMain import openApp


if __name__ ==  '__main__':
    openApp()