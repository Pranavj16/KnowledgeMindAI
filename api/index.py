import os
import sys
from pathlib import Path

# Add project root directory to python path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "rag_agent.settings")

# Optional startup migration handler for Vercel
if os.getenv("VERCEL"):
    import django
    django.setup()
    
    database_url = os.getenv("DATABASE_URL") or os.getenv("POSTGRES_URL") or os.getenv("NEON_DATABASE_URL")
    
    # If using local SQLite on Vercel without DATABASE_URL, prepare tmp storage
    if not database_url:
        import shutil
        tmp_db = Path("/tmp/db.sqlite3")
        local_db = BASE_DIR / "db.sqlite3"
        if not tmp_db.exists() and local_db.exists():
            try:
                shutil.copy(local_db, tmp_db)
            except Exception as e:
                print(f"Error copying template db: {e}")

    try:
        from django.core.management import call_command
        call_command("migrate", interactive=False)
    except Exception as e:
        print(f"Startup migration notice: {e}")

from rag_agent.wsgi import application

app = application

