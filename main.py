"""
Main entry point for the Team Scheduler FastAPI application.

Run with: python main.py
Or with uvicorn: uvicorn main:app --reload
"""

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "src.api.main:app", host="127.0.0.1", port=8000, reload=True, log_level="info"
    )
