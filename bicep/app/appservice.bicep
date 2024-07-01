param location string
param appServiceName string
param dockerImage string
param geminiAPI string
param streamlitPort string

resource appServicePlan 'Microsoft.Web/serverfarms@2022-03-01' = {
  name: toLower('asp-${appServiceName}')
  location: location
  kind: 'linux'
  sku: {
    name: 'B1'
  }
  properties: {
    reserved: true
  }
}

resource appService 'Microsoft.Web/sites@2022-03-01' = {
  name: appServiceName
  location: location
  kind: 'app,linux,container'
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    serverFarmId: appServicePlan.id
    // in practice it would use internal VPC
    publicNetworkAccess: 'Enabled'
    siteConfig: {
      linuxFxVersion: 'DOCKER|${dockerImage}'
      acrUseManagedIdentityCreds: true
      appSettings: [
        {
          name: 'DOCKER_ENABLE_CI'
          value: 'true'
        }
        // port forwarding
        {
          name: 'WEBSITES_PORT'
          value: streamlitPort
        }
        // set Gemini environment key
        {
          name: 'GEMINI_API_TOKEN'
          value: geminiAPI
        }
      ]
    }
  }
}

output principalId string = appService.identity.principalId
output appServiceResourceName string = appService.name
