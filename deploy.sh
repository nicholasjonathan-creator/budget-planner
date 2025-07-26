#!/bin/bash

# Budget Planner - Production Deployment Script
echo "🚀 Starting Budget Planner Production Deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if required tools are installed
check_tools() {
    echo "Checking required tools..."
    
    if ! command -v git &> /dev/null; then
        print_error "Git is not installed. Please install Git first."
        exit 1
    fi
    
    if ! command -v node &> /dev/null; then
        print_error "Node.js is not installed. Please install Node.js first."
        exit 1
    fi
    
    if ! command -v yarn &> /dev/null; then
        print_error "Yarn is not installed. Please install Yarn first."
        exit 1
    fi
    
    print_status "All required tools are installed"
}

# Setup Git repository
setup_git() {
    echo "Setting up Git repository..."
    
    if [ ! -d ".git" ]; then
        git init
        git add .
        git commit -m "Initial commit - Budget Planner v1.0"
        print_status "Git repository initialized"
    else
        print_status "Git repository already exists"
    fi
}

# Deploy backend to Railway
deploy_backend() {
    echo "🔧 Deploying backend to Railway..."
    
    cd backend
    
    # Check if Railway CLI is installed
    if ! command -v railway &> /dev/null; then
        print_warning "Railway CLI not found. Installing..."
        npm install -g @railway/cli
    fi
    
    # Login to Railway (user will need to do this manually)
    print_warning "Please login to Railway when prompted..."
    railway login
    
    # Create new project or use existing
    if [ ! -f "railway.toml" ]; then
        print_error "railway.toml not found"
        exit 1
    fi
    
    # Deploy
    railway up
    
    # Get the deployment URL
    BACKEND_URL=$(railway status | grep "https://" | awk '{print $2}')
    
    if [ -z "$BACKEND_URL" ]; then
        print_error "Failed to get backend URL"
        exit 1
    fi
    
    print_status "Backend deployed to: $BACKEND_URL"
    
    # Update frontend environment with backend URL
    cd ../frontend
    sed -i "s|REACT_APP_BACKEND_URL=.*|REACT_APP_BACKEND_URL=$BACKEND_URL|" .env.production
    
    cd ..
}

# Deploy frontend to Vercel
deploy_frontend() {
    echo "🎨 Deploying frontend to Vercel..."
    
    cd frontend
    
    # Check if Vercel CLI is installed
    if ! command -v vercel &> /dev/null; then
        print_warning "Vercel CLI not found. Installing..."
        npm install -g vercel
    fi
    
    # Build the application
    yarn build
    
    # Deploy to Vercel
    vercel --prod
    
    # Get the deployment URL
    FRONTEND_URL=$(vercel --prod 2>&1 | grep -o 'https://[^[:space:]]*')
    
    if [ -z "$FRONTEND_URL" ]; then
        print_error "Failed to get frontend URL"
        exit 1
    fi
    
    print_status "Frontend deployed to: $FRONTEND_URL"
    
    cd ..
}

# Setup MongoDB Atlas
setup_mongodb() {
    echo "🗄️  Setting up MongoDB Atlas..."
    
    print_warning "Please complete MongoDB Atlas setup manually:"
    echo "1. Go to https://cloud.mongodb.com/"
    echo "2. Create a free account"
    echo "3. Create a new cluster"
    echo "4. Create database user"
    echo "5. Whitelist IP addresses (0.0.0.0/0 for development)"
    echo "6. Get connection string"
    echo "7. Update MONGO_URL in backend environment variables"
    
    read -p "Press Enter when MongoDB Atlas setup is complete..."
}

# Main deployment flow
main() {
    echo "🚀 Budget Planner Production Deployment"
    echo "========================================"
    
    check_tools
    setup_git
    setup_mongodb
    deploy_backend
    deploy_frontend
    
    echo ""
    echo "🎉 Deployment Complete!"
    echo "======================="
    echo "Frontend: $FRONTEND_URL"
    echo "Backend: $BACKEND_URL"
    echo ""
    echo "Next steps:"
    echo "1. Setup custom domain (optional)"
    echo "2. Configure SMS webhooks"
    echo "3. Add authentication"
    echo "4. Setup monitoring"
    echo ""
    print_status "Your Budget Planner is now live! 🎉"
}

# Run main function
main