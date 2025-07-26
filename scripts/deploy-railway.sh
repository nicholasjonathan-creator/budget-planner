#!/bin/bash

# Automated Railway Deployment Script for Budget Planner
# This script deploys both backend and frontend to Railway with proper configuration

set -e

echo "🚂 Budget Planner - Railway Deployment"
echo "======================================"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
PROJECT_NAME="budget-planner"
BACKEND_SERVICE="budget-planner-backend"
FRONTEND_SERVICE="budget-planner-frontend"

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

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    print_warning "Railway CLI not found. Installing..."
    npm install -g @railway/cli
    print_status "Railway CLI installed"
fi

# Check if user is logged in
if ! railway whoami &> /dev/null; then
    print_error "Please login to Railway first:"
    echo "railway login"
    exit 1
fi

print_status "Railway CLI ready"

# Validate environment variables
echo ""
print_info "Validating environment variables..."

required_vars=(
    "MONGO_URL"
    "SENDGRID_API_KEY" 
    "JWT_SECRET"
    "SENDER_EMAIL"
)

missing_vars=()
for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        missing_vars+=("$var")
    fi
done

if [ ${#missing_vars[@]} -ne 0 ]; then
    print_error "Missing required environment variables:"
    for var in "${missing_vars[@]}"; do
        echo "   - $var"
    done
    echo ""
    echo "Please set them and run again:"
    echo "export MONGO_URL='your_mongodb_url'"
    echo "export SENDGRID_API_KEY='your_sendgrid_key'"
    echo "export JWT_SECRET='your_jwt_secret'"
    echo "export SENDER_EMAIL='your_sender_email'"
    exit 1
fi

print_status "Environment variables validated"

# Create project if it doesn't exist
echo ""
print_info "Setting up Railway project..."

if ! railway status &> /dev/null; then
    print_info "Creating new Railway project..."
    railway init --name "$PROJECT_NAME"
    print_status "Railway project created: $PROJECT_NAME"
else
    print_status "Using existing Railway project"
fi

# Deploy Backend
echo ""
print_info "Deploying Backend Service..."
echo "============================"

cd backend

# Create railway.json for backend
cat > railway.json << EOF
{
  "deploy": {
    "startCommand": "uvicorn server:app --host 0.0.0.0 --port \$PORT",
    "healthcheckPath": "/api/health",
    "healthcheckTimeout": 100,
    "restartPolicyType": "on_failure",
    "restartPolicyMaxRetries": 3
  }
}
EOF

# Deploy backend
print_info "Deploying backend to Railway..."
railway up --detach

# Set backend environment variables
print_info "Setting backend environment variables..."
railway variables set ENVIRONMENT=production
railway variables set MONGO_URL="$MONGO_URL"
railway variables set SENDGRID_API_KEY="$SENDGRID_API_KEY"
railway variables set JWT_SECRET="$JWT_SECRET"
railway variables set SENDER_EMAIL="$SENDER_EMAIL"
railway variables set SENDER_NAME="Budget Planner"
railway variables set ENABLE_EMAIL_SENDING=true
railway variables set LOG_LEVEL=INFO
railway variables set ACCESS_TOKEN_EXPIRE=1440

print_status "Backend environment variables set"

# Get backend URL
BACKEND_URL=$(railway domain)
if [ -z "$BACKEND_URL" ]; then
    print_warning "Backend domain not ready yet. Please get it from Railway dashboard."
    BACKEND_URL="https://your-backend.railway.app"
fi

print_info "Backend URL: $BACKEND_URL"

cd ..

# Deploy Frontend
echo ""
print_info "Deploying Frontend Service..."
echo "============================"

cd frontend

# Create railway.json for frontend
cat > railway.json << EOF
{
  "deploy": {
    "buildCommand": "yarn install && yarn build",
    "startCommand": "npx serve -s build -l \$PORT",
    "healthcheckPath": "/",
    "healthcheckTimeout": 100
  }
}
EOF

# Set frontend environment variables
print_info "Setting frontend environment variables..."

# Create production environment file
cat > .env.production << EOF
REACT_APP_BACKEND_URL=$BACKEND_URL
REACT_APP_ENVIRONMENT=production
GENERATE_SOURCEMAP=false
EOF

# Deploy frontend
print_info "Deploying frontend to Railway..."
railway init --name "$FRONTEND_SERVICE"
railway up --detach

print_status "Frontend deployed"

# Get frontend URL
FRONTEND_URL=$(railway domain)
if [ -z "$FRONTEND_URL" ]; then
    print_warning "Frontend domain not ready yet. Please get it from Railway dashboard."
    FRONTEND_URL="https://your-frontend.railway.app"
fi

print_info "Frontend URL: $FRONTEND_URL"

cd ..

# Update CORS origins in backend
echo ""
print_info "Updating CORS configuration..."

cd backend
railway variables set CORS_ORIGINS="[\"$FRONTEND_URL\"]"
print_status "CORS origins updated"
cd ..

# Create deployment summary
echo ""
print_status "Deployment completed successfully!"
echo ""
echo "📋 Deployment Summary:"
echo "====================="
echo "🔗 Frontend URL: $FRONTEND_URL"
echo "🔗 Backend URL: $BACKEND_URL"
echo ""
echo "🔧 Next Steps:"
echo "1. Update your domain DNS if using custom domain"
echo "2. Complete SendGrid sender verification"
echo "3. Test the application thoroughly"
echo "4. Monitor logs: railway logs"
echo ""
echo "🔍 Health Check:"
echo "   Backend: $BACKEND_URL/api/health"
echo "   Frontend: $FRONTEND_URL"
echo ""
echo "📊 Monitoring:"
echo "   railway logs --service $BACKEND_SERVICE"
echo "   railway logs --service $FRONTEND_SERVICE"
echo ""

# Save deployment info
cat > deployment-info.json << EOF
{
  "deployment_date": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "platform": "railway",
  "backend_url": "$BACKEND_URL",
  "frontend_url": "$FRONTEND_URL",
  "backend_service": "$BACKEND_SERVICE",
  "frontend_service": "$FRONTEND_SERVICE",
  "project_name": "$PROJECT_NAME"
}
EOF

print_status "Deployment information saved to deployment-info.json"

# Offer to run health check
echo ""
read -p "Would you like to run a health check now? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_info "Running health check..."
    
    # Wait a bit for services to start
    sleep 10
    
    # Check backend health
    if curl -f "$BACKEND_URL/api/health" > /dev/null 2>&1; then
        print_status "Backend health check passed"
    else
        print_warning "Backend health check failed - services might still be starting"
    fi
    
    # Check frontend
    if curl -f "$FRONTEND_URL" > /dev/null 2>&1; then
        print_status "Frontend health check passed"
    else
        print_warning "Frontend health check failed - services might still be starting"
    fi
fi

echo ""
print_status "Railway deployment completed! 🎉"
echo ""
echo "Your Budget Planner is now live at: $FRONTEND_URL"