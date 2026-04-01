// infra/integration/service_bus.bicep
// Azure Service Bus namespace with queues for AegisAP integration.
// Uses Premium SKU for private endpoint support and 99.9% SLA.

param location string
param namespaceName string

@description('SKU: Standard for dev, Premium for prod (required for private endpoints)')
@allowed(['Standard', 'Premium'])
param sku string = 'Premium'

param invoiceQueueName string = 'invoice-submissions'
param invoiceReplyQueueName string = 'invoice-results'
param dlqRedriveTopicName string = 'dlq-redrive'

resource serviceBusNamespace 'Microsoft.ServiceBus/namespaces@2022-10-01-preview' = {
  name: namespaceName
  location: location
  sku: {
    name: sku
    tier: sku
    capacity: 1
  }
  properties: {
    disableLocalAuth: true // enforce MI/RBAC only — no connection strings
    publicNetworkAccess: 'Disabled'
    minimumTlsVersion: '1.2'
  }
}

resource invoiceQueue 'Microsoft.ServiceBus/namespaces/queues@2022-10-01-preview' = {
  parent: serviceBusNamespace
  name: invoiceQueueName
  properties: {
    maxDeliveryCount: 5
    lockDuration: 'PT2M'
    deadLetteringOnMessageExpiration: true
    enablePartitioning: false // required false for Premium geo-replication
    defaultMessageTimeToLive: 'P1D'
  }
}

resource invoiceReplyQueue 'Microsoft.ServiceBus/namespaces/queues@2022-10-01-preview' = {
  parent: serviceBusNamespace
  name: invoiceReplyQueueName
  properties: {
    maxDeliveryCount: 3
    lockDuration: 'PT1M'
    deadLetteringOnMessageExpiration: true
    enablePartitioning: false
    defaultMessageTimeToLive: 'PT1H'
  }
}

resource dlqRedriveTopic 'Microsoft.ServiceBus/namespaces/topics@2022-10-01-preview' = {
  parent: serviceBusNamespace
  name: dlqRedriveTopicName
  properties: {
    defaultMessageTimeToLive: 'P7D'
    maxSizeInMegabytes: 1024
  }
}

output namespaceId string = serviceBusNamespace.id
output namespaceName string = serviceBusNamespace.name
output namespaceHostname string = '${serviceBusNamespace.name}.servicebus.windows.net'
output invoiceQueueId string = invoiceQueue.id
output invoiceReplyQueueId string = invoiceReplyQueue.id
