#!/bin/bash

echo "🚀 Deploying Budget Planner Backend to Railway..."

# Create railway.toml with the correct config
cat > /app/backend/railway.toml << 'EOF'
[build]
builder = "dockerfile"

[deploy]
startCommand = "uvicorn server:app --host 0.0.0.0 --port $PORT"
restartPolicyType = "always"
healthcheckPath = "/api/health"
healthcheckTimeout = 30

[env]
PORT = "8000"
EOF

# Create production Dockerfile
cat > /app/backend/Dockerfile << 'EOF'
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/api/health || exit 1

# Start application
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
EOF

echo "✅ Railway configuration files created"
echo "📦 Backend is ready for deployment"
echo ""
echo "🎯 Next steps:"
echo "1. Install Railway CLI: npm install -g @railway/cli"
echo "2. Login to Railway: railway login"
echo "3. Deploy: cd backend && railway up"
echo "4. Set environment variables in Railway dashboard"
echo ""
echo "💡 Your MongoDB connection string is ready!"
echo "🔒 MongoDB URL: mongodb+srv://your-username:your-password@your-cluster.mongodb.net/budget_planner?retryWrites=true&w=majority&appName=YourAppName"
EOF

chmod +x /app/railway-deploy.sh
/app/railway-deploy.sh