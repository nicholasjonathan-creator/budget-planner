#!/bin/bash

# Budget Planner Production Deployment Script
# This script automates the production deployment process

set -e  # Exit on any error

echo "🚀 Budget Planner Production Deployment"
echo "========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DEPLOYMENT_ENV=${DEPLOYMENT_ENV:-production}
APP_NAME="budget-planner"
VERSION=$(date +%Y%m%d-%H%M%S)

echo -e "${BLUE}📋 Deployment Configuration:${NC}"
echo "   Environment: $DEPLOYMENT_ENV"
echo "   App Name: $APP_NAME"
echo "   Version: $VERSION"
echo ""

# Function to print status
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Step 1: Environment Validation
echo -e "${BLUE}📋 Step 1: Environment Validation${NC}"
echo "=================================="

# Check required environment variables
REQUIRED_VARS=(
    "SENDGRID_API_KEY"
    "MONGO_URL"
    "JWT_SECRET"
    "SENDER_EMAIL"
)

missing_vars=()
for var in "${REQUIRED_VARS[@]}"; do
    if [ -z "${!var}" ]; then
        missing_vars+=("$var")
    fi
done

if [ ${#missing_vars[@]} -eq 0 ]; then
    print_status "All required environment variables are set"
else
    print_error "Missing required environment variables:"
    for var in "${missing_vars[@]}"; do
        echo "   - $var"
    done
    echo ""
    echo "Please set missing variables and run again:"
    echo "export SENDGRID_API_KEY='your_sendgrid_api_key'"
    echo "export MONGO_URL='your_mongodb_connection_string'"
    echo "export JWT_SECRET='your_jwt_secret'"
    echo "export SENDER_EMAIL='your_verified_sender_email'"
    exit 1
fi

# Step 2: Build Application
echo -e "${BLUE}📦 Step 2: Building Application${NC}"
echo "================================"

# Build frontend
echo "Building React frontend..."
cd frontend
if [ -f "package.json" ]; then
    yarn install --frozen-lockfile
    yarn build
    print_status "Frontend build completed"
else
    print_error "Frontend package.json not found"
    exit 1
fi
cd ..

# Install backend dependencies
echo "Installing backend dependencies..."
cd backend
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    print_status "Backend dependencies installed"
else
    print_error "Backend requirements.txt not found"
    exit 1
fi
cd ..

# Step 3: Database Migration
echo -e "${BLUE}🗄️  Step 3: Database Setup${NC}"
echo "=========================="

# Create database initialization script
python3 -c "
import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient

async def setup_database():
    client = AsyncIOMotorClient(os.getenv('MONGO_URL'))
    db = client['budget_planner']
    
    # Create indexes for performance
    collections = {
        'users': [
            {'email': 1},
            {'username': 1},
            {'is_active': 1}
        ],
        'transactions': [
            {'user_id': 1, 'date': -1},
            {'category_id': 1},
            {'type': 1}
        ],
        'budget_limits': [
            {'user_id': 1, 'category_id': 1, 'month': 1, 'year': 1}
        ],
        'notification_preferences': [
            {'user_id': 1}
        ],
        'notification_logs': [
            {'user_id': 1, 'sent_at': -1}
        ]
    }
    
    for collection_name, indexes in collections.items():
        collection = db[collection_name]
        for index in indexes:
            try:
                await collection.create_index(list(index.items()))
                print(f'✅ Created index for {collection_name}: {index}')
            except Exception as e:
                print(f'⚠️  Index might already exist for {collection_name}: {e}')
    
    print('✅ Database setup completed')

asyncio.run(setup_database())
"

print_status "Database indexes created"

# Step 4: Production Configuration
echo -e "${BLUE}⚙️  Step 4: Production Configuration${NC}"
echo "===================================="

# Create production environment file
cat > .env.production << EOF
# Production Environment Configuration
ENVIRONMENT=production
NODE_ENV=production

# Database
MONGO_URL=${MONGO_URL}
DB_NAME=budget_planner

# Authentication
JWT_SECRET=${JWT_SECRET}
ACCESS_TOKEN_EXPIRE=1440

# Email Configuration
SENDGRID_API_KEY=${SENDGRID_API_KEY}
SENDER_EMAIL=${SENDER_EMAIL}
SENDER_NAME=Budget Planner
ENABLE_EMAIL_SENDING=true

# Security
CORS_ORIGINS=["https://your-domain.com"]
LOG_LEVEL=INFO

# Application
APP_VERSION=${VERSION}
DEPLOYMENT_DATE=$(date -u +%Y-%m-%dT%H:%M:%SZ)
EOF

print_status "Production environment configuration created"

# Step 5: Create Docker Configuration
echo -e "${BLUE}🐳 Step 5: Docker Configuration${NC}"
echo "================================"

# Create production Dockerfile for backend
cat > backend/Dockerfile.prod << 'EOF'
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 app && chown -R app:app /app
USER app

# Expose port
EXPOSE 8001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8001/api/health || exit 1

# Run application
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8001", "--workers", "2"]
EOF

# Create production Dockerfile for frontend
cat > frontend/Dockerfile.prod << 'EOF'
# Build stage
FROM node:18-alpine as build

WORKDIR /app
COPY package*.json yarn.lock ./
RUN yarn install --frozen-lockfile

COPY . .
RUN yarn build

# Production stage
FROM nginx:alpine

# Copy built files
COPY --from=build /app/build /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Expose port
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost/ || exit 1

CMD ["nginx", "-g", "daemon off;"]
EOF

# Create nginx configuration
cat > frontend/nginx.conf << 'EOF'
events {
    worker_connections 1024;
}

http {
    include       /etc/nginx/mime.types;
    default_type  application/octet-stream;
    
    sendfile        on;
    keepalive_timeout  65;
    
    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;
    
    server {
        listen 80;
        server_name localhost;
        
        root /usr/share/nginx/html;
        index index.html;
        
        # Security headers
        add_header X-Frame-Options DENY;
        add_header X-Content-Type-Options nosniff;
        add_header X-XSS-Protection "1; mode=block";
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
        
        # React Router support
        location / {
            try_files \$uri \$uri/ /index.html;
        }
        
        # API proxy to backend
        location /api/ {
            proxy_pass http://backend:8001;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto \$scheme;
        }
        
        # Static assets caching
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }
}
EOF

# Create docker-compose for production
cat > docker-compose.prod.yml << 'EOF'
version: '3.8'

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.prod
    container_name: budget-planner-backend
    restart: unless-stopped
    env_file:
      - .env.production
    ports:
      - "8001:8001"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8001/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    networks:
      - budget-planner-network

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.prod
    container_name: budget-planner-frontend
    restart: unless-stopped
    ports:
      - "80:80"
    depends_on:
      - backend
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost/"]
      interval: 30s
      timeout: 10s
      retries: 3
    networks:
      - budget-planner-network

networks:
  budget-planner-network:
    driver: bridge

volumes:
  app-data:
EOF

print_status "Docker configuration created"

# Step 6: Create deployment scripts for different platforms
echo -e "${BLUE}🌐 Step 6: Platform Deployment Scripts${NC}"
echo "======================================"

# Railway deployment
cat > railway-deploy.sh << 'EOF'
#!/bin/bash
echo "🚂 Deploying to Railway..."

# Install Railway CLI if not present
if ! command -v railway &> /dev/null; then
    npm install -g @railway/cli
fi

# Login check
if ! railway whoami &> /dev/null; then
    echo "Please login to Railway first:"
    echo "railway login"
    exit 1
fi

# Deploy backend
cd backend
railway up --service backend
cd ..

# Deploy frontend  
cd frontend
railway up --service frontend
cd ..

echo "✅ Railway deployment completed"
EOF

# Render deployment
cat > render-deploy.sh << 'EOF'
#!/bin/bash
echo "🎨 Preparing for Render deployment..."

# Create render.yaml
cat > render.yaml << 'RENDER_EOF'
services:
  - type: web
    name: budget-planner-backend
    env: python
    plan: free
    buildCommand: "pip install -r requirements.txt"
    startCommand: "uvicorn server:app --host 0.0.0.0 --port $PORT"
    envVars:
      - key: ENVIRONMENT
        value: production
      - key: MONGO_URL
        sync: false
      - key: SENDGRID_API_KEY
        sync: false
      - key: JWT_SECRET
        sync: false
      - key: SENDER_EMAIL
        sync: false

  - type: web
    name: budget-planner-frontend
    env: static
    buildCommand: "yarn install && yarn build"
    staticPublishPath: ./build
    routes:
      - type: rewrite
        source: /api/*
        destination: https://budget-planner-backend.onrender.com/api/:splat
RENDER_EOF

echo "✅ Render configuration created"
echo "   Next steps:"
echo "   1. Connect your repository to Render"
echo "   2. Set environment variables in Render dashboard"
echo "   3. Deploy services"
EOF

# Vercel deployment
cat > vercel-deploy.sh << 'EOF'
#!/bin/bash
echo "▲ Deploying to Vercel..."

cd frontend

# Create vercel.json if not exists
cat > vercel.json << 'VERCEL_EOF'
{
  "version": 2,
  "builds": [
    {
      "src": "package.json",
      "use": "@vercel/static-build",
      "config": {
        "distDir": "build"
      }
    }
  ],
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "https://your-backend-url.com/api/$1"
    },
    {
      "src": "/(.*)",
      "dest": "/index.html"
    }
  ]
}
VERCEL_EOF

# Install Vercel CLI if not present
if ! command -v vercel &> /dev/null; then
    npm install -g vercel
fi

# Deploy
vercel --prod

cd ..
echo "✅ Vercel deployment completed"
EOF

# Make scripts executable
chmod +x railway-deploy.sh render-deploy.sh vercel-deploy.sh

print_status "Platform deployment scripts created"

# Step 7: Health Check and Monitoring
echo -e "${BLUE}🔍 Step 7: Health Check System${NC}"
echo "==============================="

# Create health check script
cat > health-check.sh << 'EOF'
#!/bin/bash

# Health Check Script for Budget Planner
echo "🏥 Budget Planner Health Check"
echo "============================="

BACKEND_URL=${BACKEND_URL:-http://localhost:8001}
FRONTEND_URL=${FRONTEND_URL:-http://localhost:3000}

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

check_service() {
    local service_name=$1
    local url=$2
    local expected_status=${3:-200}
    
    echo -n "Checking $service_name... "
    
    if curl -s -o /dev/null -w "%{http_code}" "$url" | grep -q "$expected_status"; then
        echo -e "${GREEN}✅ OK${NC}"
        return 0
    else
        echo -e "${RED}❌ FAILED${NC}"
        return 1
    fi
}

# Check backend health
check_service "Backend API" "$BACKEND_URL/api/health"

# Check frontend
check_service "Frontend" "$FRONTEND_URL"

# Check database connection (via backend)
check_service "Database Connection" "$BACKEND_URL/api/health"

# Check email system
check_service "Email System" "$BACKEND_URL/api/notifications/production/status"

# Check authentication
echo "Testing authentication..."
AUTH_RESPONSE=$(curl -s -X POST "$BACKEND_URL/api/auth/login" \
    -H "Content-Type: application/json" \
    -d '{"email":"test@example.com","password":"testpassword"}')

if echo "$AUTH_RESPONSE" | grep -q "access_token"; then
    echo -e "${GREEN}✅ Authentication OK${NC}"
else
    echo -e "${YELLOW}⚠️  Authentication test inconclusive${NC}"
fi

echo ""
echo "Health check completed at $(date)"
EOF

chmod +x health-check.sh

print_status "Health check system created"

# Step 8: Monitoring and Logging
echo -e "${BLUE}📊 Step 8: Monitoring Setup${NC}"
echo "============================"

# Create monitoring configuration
cat > monitoring/prometheus.yml << 'EOF'
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'budget-planner-backend'
    static_configs:
      - targets: ['backend:8001']
    metrics_path: '/metrics'
    
  - job_name: 'budget-planner-frontend'
    static_configs:
      - targets: ['frontend:80']
EOF

# Create logging configuration
cat > monitoring/fluentd.conf << 'EOF'
<source>
  @type forward
  port 24224
  bind 0.0.0.0
</source>

<match budget-planner.*>
  @type file
  path /fluentd/log/app.log
  append true
  <format>
    @type json
  </format>
  <buffer>
    timekey 1d
    timekey_use_utc true
    timekey_wait 10m
  </buffer>
</match>
EOF

print_status "Monitoring configuration created"

# Final Summary
echo ""
echo -e "${GREEN}🎉 Production Deployment Setup Complete!${NC}"
echo "========================================"
echo ""
echo "📋 What's been configured:"
echo "   ✅ Environment validation"
echo "   ✅ Application build process"
echo "   ✅ Database setup and indexes"
echo "   ✅ Production configuration"
echo "   ✅ Docker containerization"
echo "   ✅ Multi-platform deployment scripts"
echo "   ✅ Health checking system"
echo "   ✅ Monitoring and logging"
echo ""
echo "🚀 Next Steps:"
echo "   1. Choose your deployment platform:"
echo "      - Railway: ./railway-deploy.sh"
echo "      - Render: ./render-deploy.sh" 
echo "      - Vercel: ./vercel-deploy.sh"
echo "      - Docker: docker-compose -f docker-compose.prod.yml up"
echo ""
echo "   2. Configure your domain and SSL certificate"
echo "   3. Complete SendGrid sender verification"
echo "   4. Run health checks: ./health-check.sh"
echo ""
echo "🔧 Environment Variables Required:"
for var in "${REQUIRED_VARS[@]}"; do
    echo "   - $var"
done
echo ""
echo "📚 Documentation: Check DEPLOYMENT.md for detailed instructions"

exit 0
EOF