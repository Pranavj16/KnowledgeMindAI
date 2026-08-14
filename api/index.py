import os
import sys
import shutil
from pathlib import Path

# Add project root directory to python path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

# On Vercel serverless environment, copy SQLite database to writable /tmp directory if needed
if os.getenv("VERCEL"):
    tmp_db = Path("/tmp/db.sqlite3")
    local_db = BASE_DIR / "db.sqlite3"
    if not tmp_db.exists() and local_db.exists():
        try:
            shutil.copy(local_db, tmp_db)
        except Exception as e:
            print(f"Error initializing /tmp/db.sqlite3: {e}")

from rag_agent.wsgi import application

app = application
