#!/bin/bash

# Simple deployment script for Azure App Service
# Requires Azure CLI (az) to be installed and logged in

# Configuration
RESOURCE_GROUP="minimusic-rg"
APP_SERVICE_PLAN="minimusic-plan"
WEB_APP_NAME="minimusic-app-$RANDOM"
LOCATION="eastus"

echo "🚀 Starting Azure Deployment..."

# Create resource group
echo "Creating resource group: $RESOURCE_GROUP..."
az group create --name $RESOURCE_GROUP --location $LOCATION

# Create app service plan (Free tier)
echo "Creating App Service Plan (F1 Free Tier)..."
az appservice plan create --name $APP_SERVICE_PLAN --resource-group $RESOURCE_GROUP --sku F1 --is-linux

# Create web app
echo "Creating Web App: $WEB_APP_NAME..."
az webapp create --resource-group $RESOURCE_GROUP --plan $APP_SERVICE_PLAN --name $WEB_APP_NAME --runtime "PYTHON:3.9"

# Configure environment variables
echo "Configuring environment variables..."
az webapp config appsettings set --resource-group $RESOURCE_GROUP --name $WEB_APP_NAME --settings \
    AZURE_STORAGE_CONNECTION_STRING="your_connection_string" \
    AZURE_STORAGE_CONTAINER_NAME="music-container" \
    FLASK_APP="app.py"

echo "✅ App created! You can now deploy your code using:"
echo "az webapp up --name $WEB_APP_NAME"
