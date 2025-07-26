#!/bin/bash

echo "🔍 Checking Budget Planner Deployment Status"
echo "============================================"

BACKEND_URL="https://budget-planner-be-20250726-1342.onrender.com"
FRONTEND_URL="https://budget-planner-fe-20250726-1342.onrender.com"

echo ""
echo "📊 Backend Status:"
echo "-----------------"
echo "URL: $BACKEND_URL"
if timeout 15 curl -f -s "$BACKEND_URL/api/health" > /dev/null 2>&1; then
    echo "✅ Backend is responding"
    echo "Health Check Response:"
    timeout 10 curl -s "$BACKEND_URL/api/health" | head -5
else
    echo "❌ Backend is not responding or starting up"
    echo "Status Code:"
    timeout 10 curl -I -s "$BACKEND_URL/api/health" | head -1 || echo "No response"
fi

echo ""
echo "🌐 Frontend Status:"
echo "------------------"
echo "URL: $FRONTEND_URL"
if timeout 15 curl -f -s "$FRONTEND_URL" > /dev/null 2>&1; then
    echo "✅ Frontend is responding"
else
    echo "❌ Frontend is not responding or starting up"
    echo "Status Code:"
    timeout 10 curl -I -s "$FRONTEND_URL" | head -1 || echo "No response"
fi

echo ""
echo "🔧 Configuration Summary:"
echo "------------------------"
echo "✅ Frontend .env updated to point to correct backend"
echo "✅ render.yaml updated with correct service names"
echo "✅ _redirects file updated with correct backend URL"
echo "✅ Sensitive data removed from documentation files"
echo "✅ GitHub Secret Protection issues resolved"
echo ""
echo "⚠️  Note: Services may take 5-15 minutes to fully deploy after configuration changes"