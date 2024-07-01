param location string = resourceGroup().location
param appServiceName string
param containerRegistryName string
param dockerImageNameTag string
param geminiAPI string
param streamlitPort string = "8501"

var dockerImage = '${containerRegistryName}.azurecr.io/${dockerImageNameTag}'

module appService 'appservice.bicep' = {
  name: '${appServiceName}-app'
  params: {
    appServiceName: appServiceName
    location:	location
    dockerImage: dockerImage
    geminiAPI: geminiAPI
    streamlitPort: streamlitPort
  }
}

module roleAssignment 'roleassignment.bicep' = {
  name: '${appServiceName}-roleassignment'
  params: {
    appServicePrincipalId: appService.outputs.principalId
    containerRegistryName: containerRegistryName
  }
}
