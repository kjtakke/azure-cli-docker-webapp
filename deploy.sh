#!/bin/bash

# =======================
# Azure Container Deploy
# =======================

# Default Variables
AZURE_RESOURCE_GROUP="default-group"
AZURE_REGISTRY_NAME="myregistry"
AZURE_IMAGE_NAME="myapp"
AZURE_CONTAINER_NAME="myapp-instance"
AZURE_LOCATION="australiaeast"
AZURE_CPU="1"
AZURE_MEMORY="1.5"
AZURE_PORT="80"
AZURE_DNS_LABEL="myapp"
AZURE_TAG="latest"
AZURE_PASSWORD="changeme"

# Parse arguments
while [ "$#" -gt 0 ]; do
  case "$1" in
    --group) AZURE_RESOURCE_GROUP="$2"; shift 2;;
    --registry) AZURE_REGISTRY_NAME="$2"; shift 2;;
    --image) AZURE_IMAGE_NAME="$2"; shift 2;;
    --container) AZURE_CONTAINER_NAME="$2"; shift 2;;
    --location) AZURE_LOCATION="$2"; shift 2;;
    --cpu) AZURE_CPU="$2"; shift 2;;
    --memory) AZURE_MEMORY="$2"; shift 2;;
    --port) AZURE_PORT="$2"; shift 2;;
    --dns) AZURE_DNS_LABEL="$2"; shift 2;;
    --tag) AZURE_TAG="$2"; shift 2;;
    --password) AZURE_PASSWORD="$2"; shift 2;;
    --restart) RESTART_ONLY=true; shift;;
    --delete-image) DELETE_IMAGE=true; shift;;
    --delete-container) DELETE_CONTAINER=true; shift;;
    *) echo "Unknown flag: $1"; exit 1;;
  esac
done

# Derived values
FULL_IMAGE="${AZURE_REGISTRY_NAME}.azurecr.io/${AZURE_IMAGE_NAME}:${AZURE_TAG}"

# Azure login (interactive)
echo "🔐 Logging into Azure..."
az login

echo "🔐 Logging into ACR..."
az acr login --name "$AZURE_REGISTRY_NAME"

# Optional delete steps
[ "$DELETE_IMAGE" = true ] && az acr repository delete --name "$AZURE_REGISTRY_NAME" --repository "$AZURE_IMAGE_NAME" --yes
[ "$DELETE_CONTAINER" = true ] && az container delete --name "$AZURE_CONTAINER_NAME" --resource-group "$AZURE_RESOURCE_GROUP" --yes

# Restart only mode
if [ "$RESTART_ONLY" = true ]; then
  echo "🔄 Restarting container..."
  az container restart --name "$AZURE_CONTAINER_NAME" --resource-group "$AZURE_RESOURCE_GROUP"
  exit $?
fi

# Upload Docker image
echo "📦 Tagging and pushing Docker image..."
docker tag "${AZURE_IMAGE_NAME}:${AZURE_TAG}" "$FULL_IMAGE"
docker push "$FULL_IMAGE"

# Create Azure Container Instance
echo "🚀 Creating Azure container instance..."
az container create \
  --name "$AZURE_CONTAINER_NAME" \
  --resource-group "$AZURE_RESOURCE_GROUP" \
  --image "$FULL_IMAGE" \
  --cpu "$AZURE_CPU" \
  --memory "$AZURE_MEMORY" \
  --registry-login-server "${AZURE_REGISTRY_NAME}.azurecr.io" \
  --registry-username "$AZURE_REGISTRY_NAME" \
  --registry-password "$AZURE_PASSWORD" \
  --dns-name-label "$AZURE_DNS_LABEL" \
  --ports "$AZURE_PORT" \
  --os-type Linux \
  --location "$AZURE_LOCATION"
