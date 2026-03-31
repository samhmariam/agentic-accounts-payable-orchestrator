targetScope = 'resourceGroup'

param location string = resourceGroup().location
param logAnalyticsWorkspaceId string

resource retrySpikeAlert 'Microsoft.Insights/scheduledQueryRules@2023-12-01' = {
  name: 'aegisap-retry-spike'
  location: location
  properties: {
    description: 'Retry spikes detected for AegisAP workflow dependencies.'
    enabled: true
    evaluationFrequency: 'PT15M'
    windowSize: 'PT15M'
    scopes: [
      logAnalyticsWorkspaceId
    ]
    severity: 2
    criteria: {
      allOf: [
        {
          query: 'AppTraces | where Message contains "retry_" | summarize Count=count()'
          timeAggregation: 'Count'
          operator: 'GreaterThan'
          threshold: 10
          failingPeriods: {
            numberOfEvaluationPeriods: 1
            minFailingPeriodsToAlert: 1
          }
        }
      ]
    }
    targetResourceTypes: [
      'microsoft.operationalinsights/workspaces'
    ]
  }
}

resource latencyAlert 'Microsoft.Insights/scheduledQueryRules@2023-12-01' = {
  name: 'aegisap-node-latency'
  location: location
  properties: {
    description: 'P95 node latency breached for AegisAP.'
    enabled: true
    evaluationFrequency: 'PT15M'
    windowSize: 'PT15M'
    scopes: [
      logAnalyticsWorkspaceId
    ]
    severity: 2
    criteria: {
      allOf: [
        {
          query: 'AppTraces | summarize Count=count()'
          timeAggregation: 'Count'
          operator: 'GreaterThan'
          threshold: 0
          failingPeriods: {
            numberOfEvaluationPeriods: 1
            minFailingPeriodsToAlert: 1
          }
        }
      ]
    }
    targetResourceTypes: [
      'microsoft.operationalinsights/workspaces'
    ]
  }
}

output retrySpikeAlertId string = retrySpikeAlert.id
output latencyAlertId string = latencyAlert.id
