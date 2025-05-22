metadata description = 'Sets up private networking for all resources, using VNet, private endpoints, and DNS zones.'

@description('The name of the VNet to create')
param vnetName string

@description('The location to create the VNet and private endpoints')
param location string = resourceGroup().location

@description('The tags to apply to all resources')
param tags object = {}

@description('The name of an existing App Service Plan to connect to the VNet')
param appServicePlanName string

@description('The name of the Azure Container Apps environment to connect to the VNet')
param acaManagedEnvironmentName string

param usePrivateEndpoint bool = false

@allowed(['appservice', 'containerapps'])
param deploymentTarget string

resource appServicePlan 'Microsoft.Web/serverfarms@2022-03-01' existing = if (deploymentTarget == 'appservice') {
  name: appServicePlanName
}

var appSubnet = deploymentTarget == 'appservice' 
  ? [
      {
        name: 'app-int-subnet'
        properties: {
          addressPrefix: '10.0.2.0/24'
          privateEndpointNetworkPolicies: 'Enabled'
          privateLinkServiceNetworkPolicies: 'Enabled'
          delegations: [
            {
              id: appServicePlan.id
              name: appServicePlan.name
              properties: {
                serviceName: 'Microsoft.Web/serverFarms'
              }
            }
          ]
        }
      }

  ]
  : [
      {
        name: 'capp-subnet'
        properties: {
          addressPrefix: '10.0.2.0/24'
          privateEndpointNetworkPolicies: 'Enabled'
          privateLinkServiceNetworkPolicies: 'Enabled'
          delegations: [
            {
              name: acaManagedEnvironmentName
              properties: {
                serviceName: 'Microsoft.App/environments'
              }
            }
          ]
        }
      }

  ]

  var subnets = concat(
    [
      {
        name: 'backend-subnet'
        properties: {
          addressPrefix: '10.0.1.0/24'
          privateEndpointNetworkPolicies: 'Enabled'
          privateLinkServiceNetworkPolicies: 'Enabled'
        }
      }
    ],
    appSubnet
  )

module vnet './core/networking/vnet.bicep' = if (usePrivateEndpoint) {
  name: 'vnet'
  params: {
    name: vnetName
    location: location
    tags: tags
    subnets: subnets
  }
}


output backendSubnetId string = usePrivateEndpoint ? vnet.outputs.vnetSubnets[0].id : ''
output appSubnetId string = usePrivateEndpoint ? vnet.outputs.vnetSubnets[1].id : ''
output vnetName string = usePrivateEndpoint ? vnet.outputs.name : ''
