#!/bin/bash

# Render Deployment Status Checker
echo "🔍 Comprehensive Render Deployment Check"
echo "========================================"
echo ""

# Your service URLs
BACKEND_URL="https://budget-planner-be--20250726-1342.onrender.com"
FRONTEND_URL="https://budget-planner-fe--20250726-1342.onrender.com"

echo "🎯 Your Expected Service URLs:"
echo "Backend:  $BACKEND_URL"
echo "Frontend: $FRONTEND_URL"
echo ""

# Function to check service
check_service() {
    local name=$1
    local url=$2
    local expected_path=$3
    
    echo "🔧 Checking $name..."
    echo "URL: $url$expected_path"
    
    # Try to get response with timeout
    response=$(curl -s -w "HTTP_STATUS:%{http_code}" "$url$expected_path" --max-time 45 --connect-timeout 30)
    http_code=$(echo "$response" | grep -o "HTTP_STATUS:[0-9]*" | cut -d: -f2)
    content=$(echo "$response" | sed 's/HTTP_STATUS:[0-9]*$//')
    
    case $http_code in
        200)
            echo "✅ $name is LIVE and responding"
            if [ "$name" = "Backend" ] && echo "$content" | grep -q "healthy"; then
                echo "✅ Backend API is healthy"
            elif [ "$name" = "Frontend" ] && echo "$content" | grep -q "Budget Planner"; then
                echo "✅ Frontend loaded correctly"
            fi
            echo "Response preview: $(echo "$content" | head -c 100)..."
            ;;
        404)
            echo "⚠️  $name is deployed but returns 404"
            echo "   Possible causes:"
            echo "   - Service is still starting up"
            echo "   - Wrong root directory configuration"
            echo "   - Build files not in expected location"
            ;;
        502|503|504)
            echo "🔄 $name is deployed but not ready"
            echo "   Service might still be starting up (especially common on free tier)"
            echo "   Try refreshing in a few minutes"
            ;;
        000)
            echo "❌ $name is not accessible"
            echo "   Possible causes:"
            echo "   - Service hasn't been deployed yet"
            echo "   - Service failed to build"
            echo "   - DNS issues"
            ;;
        *)
            echo "⚠️  $name returned HTTP $http_code"
            echo "   Response: $content"
            ;;
    esac
    echo ""
}

# Check both services
check_service "Backend" "$BACKEND_URL" "/api/health"
check_service "Frontend" "$FRONTEND_URL" ""

# Additional checks
echo "🔍 Additional Diagnostic Checks:"
echo "================================"

# Check if services exist (DNS resolution)
echo "🌐 DNS Resolution Check:"
if nslookup budget-planner-be--20250726-1342.onrender.com > /dev/null 2>&1; then
    echo "✅ Backend DNS resolves"
else
    echo "❌ Backend DNS does not resolve - service might not exist"
fi

if nslookup budget-planner-fe--20250726-1342.onrender.com > /dev/null 2>&1; then
    echo "✅ Frontend DNS resolves"
else
    echo "❌ Frontend DNS does not resolve - service might not exist"
fi

echo ""
echo "📋 What to Check in Render Dashboard:"
echo "===================================="
echo "1. Go to: https://dashboard.render.com"
echo "2. Look for these services:"
echo "   📦 budget-planner-be--20250726-1342"
echo "   📦 budget-planner-fe--20250726-1342"
echo ""
echo "3. Check service status:"
echo "   🟢 Live = Service is running"
echo "   🟡 Build in Progress = Still deploying"
echo "   🔴 Build Failed = Check logs for errors"
echo "   ⚪ Not Started = Service not deployed yet"
echo ""
echo "4. If services don't exist, you need to:"
echo "   - Create the services manually in Render dashboard"
echo "   - Follow the deployment guide: YOUR_RENDER_DEPLOYMENT_GUIDE.md"
echo ""
echo "5. If services exist but show errors:"
echo "   - Click on the service name"
echo "   - Check 'Logs' tab for build/runtime errors"
echo "   - Check 'Environment' tab to ensure all variables are set"
echo ""
echo "🎯 Expected Behavior When Working:"
echo "================================="
echo "Backend Health: $BACKEND_URL/api/health"
echo "  Should return: {\"status\":\"healthy\",\"timestamp\":\"...\"}"
echo ""
echo "Frontend App: $FRONTEND_URL"
echo "  Should show: Budget Planner login page"
echo ""
echo "If you see 502/503 errors, services are deployed but starting up (free tier cold start)"
echo "This can take 30-60 seconds on first access."