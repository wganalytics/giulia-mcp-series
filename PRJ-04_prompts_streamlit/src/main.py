"""Entrypoint: lança a interface Streamlit do chat (src/chat.py)."""
import sys
import subprocess
from pathlib import Path


def main():
    chat = Path(__file__).resolve().parent / "chat.py"
    subprocess.run([sys.executable, "-m", "streamlit", "run", str(chat)])


if __name__ == "__main__":
    main()
