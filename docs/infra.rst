.. _infra:

Infrastructure
==============

The `bicep/` folder contains the Infrastructure as Code (IaC) scripts needed to deploy the Alice RAG as an App Service in Azure. Below is an explanation of the initial requirements and the steps to set up the application.

While these steps would typically be integrated into the CI/CD pipeline, to avoid Gemini API and Azure costs, the `launch.sh` script must be executed manually.

1. Obtain an Azure account. New accounts receive a $200 credit and access to the free tier. For more details, visit `Microsoft Azure <https://azure.microsoft.com/en-us/free>`_.

Install the Azure Command-line interface (CLI) using `brew <https://brew.sh/>`_ on macOS:

>>> brew install az

or using your favorite Linux package manager.

2. Open your terminal and log in to your Azure account using the Azure CLI.

>>> az login

this will open a web browser where you can enter your Azure credentials.

3. Create a Resource Group where the resources will be deployed. Here the location is set to eastern USA.

>>> az group create --location eastus --name demo-app

4. Create the container registry by executing the Bicep template from `bicep/infra/`.

>>> az deployment group create \
    --resource-group demo-app \
    --template-file ./infra/main.bicep \
    --parameters containerRegistryName=aliceragllm

5. Login to Azure Container Registry (ACR), to be able to push the Docker image.

>>> az acr login -n aliceragllm

6. Build the image (or pull the latest `amd64` from DockerHub) and push it to ACR.

>>> docker pull --platform linux/amd64 pmiron/alice-rag-llm:latest
>>> docker tag pmiron/alice-rag-llm:latest aliceragllm.azurecr.io/alice-rag-llm:latest
>>> docker push aliceragllm.azurecr.io/alice-rag-llm:latest

7. Finally, deploy the application by executing the Bicep template from `bicep/app/`. This will create the App Service, App Service Plan, and assign the role. *Note*: by default, the app is publicly accessible (`publicNetworkAccess: 'Enabled'`). To avoid extra costs, stop the App Service from the console when not in use.

>>> az deployment group create \
    --resource-group demo-app \
    --template-file ./app/main.bicep \
    --parameters \
        appServiceName=alicerag \
        containerRegistryName=aliceragllm \
        dockerImageNameTag=alice-rag-llm:latest \
        geminiAPI=$GEMINI_API_KEY

Below a screenshot of an interaction with the application deployed in Azure App Service.

.. image:: img/alicerag-azure.png
  :width: 900
  :align: left
  :alt: Screenshot of the Alice RAG deployed in Azure App Service
