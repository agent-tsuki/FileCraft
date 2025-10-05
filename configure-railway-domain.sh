#!/bin/bash

# Railway Domain Configuration Helper
# Run this script after getting your Railway domain

echo "🚂 Railway Domain Configuration Helper"
echo "======================================"
echo ""

read -p "Enter your Railway domain (e.g., filecraft-production-abc123.railway.app): " RAILWAY_DOMAIN

if [ -z "$RAILWAY_DOMAIN" ]; then
    echo "❌ Domain cannot be empty!"
    exit 1
fi

echo ""
echo "🔧 Configuration for Railway Dashboard:"
echo "======================================"
echo ""
echo "Add these environment variables in your Railway project:"
echo ""
echo "CORS_ORIGINS=[\"https://$RAILWAY_DOMAIN\"]"
echo "ALLOWED_HOSTS=[\"$RAILWAY_DOMAIN\"]"
echo ""
echo "🌐 Your API will be available at:"
echo "================================"
echo ""
echo "Main API:      https://$RAILWAY_DOMAIN"
echo "Health Check:  https://$RAILWAY_DOMAIN/health"
echo "API Docs:      https://$RAILWAY_DOMAIN/docs"
echo ""
echo "🚀 Test your API:"
echo "================"
echo ""
echo "curl https://$RAILWAY_DOMAIN/health"
echo ""
echo "✅ Copy the environment variables above to your Railway project settings!"
