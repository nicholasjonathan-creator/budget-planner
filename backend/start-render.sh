#!/bin/bash
# Render startup script with optimizations

# Run database initialization
python -c "
import asyncio
from database import init_db
asyncio.run(init_db())
"

# Start application with gunicorn for better performance
if [ "$ENVIRONMENT" = "production" ]; then
    gunicorn server:app -w 1 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT --timeout 120
else
    uvicorn server:app --host 0.0.0.0 --port $PORT
fi
