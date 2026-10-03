"""
Top-level entry point forwarding to app.main:app for deployment flexibility.
Allows both `uvicorn main:app` and `uvicorn app.main:app` on Render.
"""

from app.main import app

if __name__ == "__main__":
    import os
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
