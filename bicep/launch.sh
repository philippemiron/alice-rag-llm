#!/bin/zsh
RESOURCE_GROUP="demo-app"
REGISTRY_NAME="aliceragllm"
DOCKERHUB="pmiron"
IMAGE="alice-rag-llm:latest"
APPSERVICE_NAME="alicerag"
LOCATION="eastus"

# login
az login

# create resource group
az group create --location $LOCATION --name $RESOURCE_GROUP

# create container registry
az deployment group create \
    --resource-group $RESOURCE_GROUP \
    --template-file ./infra/main.bicep \
    --parameters containerRegistryName=$REGISTRY_NAME

# login to acr
az acr login -n $REGISTRY_NAME

# retrieve, tag, push the image
# in practice we would probably push after creating the image
docker pull --platform linux/amd64 $DOCKERHUB/$IMAGE
docker tag $DOCKERHUB/$IMAGE $REGISTRY_NAME.azurecr.io/$IMAGE
docker push $REGISTRY_NAME.azurecr.io/$IMAGE

# deploy app
az deployment group create \
    --resource-group $RESOURCE_GROUP \
    --template-file ./app/main.bicep \
    --parameters \
        appServiceName=$APPSERVICE_NAME \
        containerRegistryName=$REGISTRY_NAME \
        dockerImageNameTag=$IMAGE \
        geminiAPI=$GEMINI_API_KEY
