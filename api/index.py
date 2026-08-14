import os
import sys
import shutil
from pathlib import Path

# Add project root directory to python path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "rag_agent.settings")

# Auto-migrate SQLite on Vercel serverless Lambda startup
if os.getenv("VERCEL"):
    import django
    django.setup()
    tmp_db = Path("/tmp/db.sqlite3")
    local_db = BASE_DIR / "db.sqlite3"
    
    # Copy template db if exists, or run migrations
    if not tmp_db.exists():
        if local_db.exists():
            try:
                shutil.copy(local_db, tmp_db)
            except Exception as e:
                print(f"Error copying template db: {e}")
        
        try:
            from django.core.management import call_command
            call_command("migrate", interactive=False)
            print("Successfully ran SQLite migrations on Vercel!")
        except Exception as e:
            print(f"Auto-migration error on Vercel: {e}")

from rag_agent.wsgi import application

app = application

