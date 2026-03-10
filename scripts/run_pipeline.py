#!/usr/bin/env python3
"""Manual pipeline run script. Usage: python scripts/run_pipeline.py"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.chdir(os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.core.database import SessionLocal
from app.services.pipeline import run_pipeline

def main():
    db = SessionLocal()
    try:
        run_id = run_pipeline(db, limit_trends=5, top_n=5)
        print(f"Pipeline completed. Run ID: {run_id}")
    finally:
        db.close()

if __name__ == "__main__":
    main()
