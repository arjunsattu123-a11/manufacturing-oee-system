
import json
from pathlib import Path

from fastapi import FastAPI, HTTPException
from app.database import Base, engine
from app import models

BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Manufacturing OEE Monitoring System",
    version="1.0.0",
)


@app.get("/")
def home():
    return {"message": "Manufacturing OEE System is running!"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.get("/database-status")
def database_status():
    return {
        "database": "SQLite",
        "tables_created": True,
    }


def read_oee_report(filename):
    path = PROCESSED_DIR / filename

    if not path.exists():
        raise HTTPException(
            status_code=404,
            detail=(
                f"Report not found: {filename}. "
                "Generate the OEE report first."
            ),
        )

    try:
        with path.open("r", encoding="utf-8") as file:
            return json.load(file)
    except (json.JSONDecodeError, OSError):
        raise HTTPException(
            status_code=500,
            detail=f"Could not read report: {filename}",
        )


@app.get("/oee/machines")
def get_machine_oee():
    return read_oee_report("oee_by_machine.json")


@app.get("/oee/shifts")
def get_shift_oee():
    return read_oee_report("oee_by_machine_shift.json")
