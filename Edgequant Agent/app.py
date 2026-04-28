import os
import uvicorn
from src.competition_api import app 

if __name__ == "__main__":
    # Default port for competition often varies, using 62237 as per sample
    port = int(os.getenv("PORT", 7860))

    print(f"Starting EdgeQuantAgent API on port {port}...")
    logger.info(f"Starting EdgeQuantAgent API on port {port}...")
    uvicorn.run(app, host="0.0.0.0", port=port)
    