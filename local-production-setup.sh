#!/bin/bash

echo "🚀 Setting up LOCAL PRODUCTION environment..."

# Setup local MongoDB (if not already running)
echo "📊 Setting up local MongoDB..."
sudo systemctl start mongod || echo "MongoDB already running"

# Create production database
echo "🗄️ Creating production database..."
mongosh --eval "
use budget_planner_prod;
db.createUser({
  user: 'budgetuser',
  pwd: 'securepassword123',
  roles: [{role: 'readWrite', db: 'budget_planner_prod'}]
});
"

# Update backend environment for production
echo "🔧 Configuring backend for production..."
cd /app/backend
cat > .env << EOF
MONGO_URL=mongodb://budgetuser:securepassword123@localhost:27017/budget_planner_prod
DB_NAME=budget_planner_prod
JWT_SECRET=your-super-secret-jwt-key-for-production
ENVIRONMENT=production
LOG_LEVEL=INFO
CORS_ORIGINS=["http://localhost:3000", "https://your-domain.com"]
EOF

# Update frontend environment for production
echo "🎨 Configuring frontend for production..."
cd /app/frontend
cat > .env << EOF
REACT_APP_BACKEND_URL=http://localhost:8001
REACT_APP_NAME=Budget Planner
REACT_APP_VERSION=1.0.0
NODE_ENV=production
EOF

echo "✅ Local production setup complete!"
echo "🎯 Your app is now running in production mode locally"
echo "📱 Frontend: http://localhost:3000"
echo "🔧 Backend: http://localhost:8001"
echo "📊 API Docs: http://localhost:8001/docs"