# Preconfiguring Resources, Event Sources, and Destinations Using Helm

## Overview
This guide explains how to preconfigure event sources, destinations, and resources using Helm values. This commercial feature allows you to set up these configurations ahead of time, enabling seamless deployment and operation.

## Prerequisites
- Helm installed on your system.
- Access to the graphical user interface (GUI) to retrieve the JSON configuration for resources, event sources, and destinations.

## Steps to Preconfigure Resources, Event Sources, and Destinations

### Step 1: Retrieve JSON Configuration
First, you need to obtain the JSON configuration for your resources, event sources, and destinations from the GUI. This configuration is essential as it will be used to define the preconfigured settings in your Helm chart.

### Step 2: Define Helm Values
To preconfigure these settings using Helm, you will need to modify your Helm values file. Here is how you can do it:

1. **Configuration Structure:**
    ```yaml
    config:
      preConfiguration:
        eventSources: |-
          {
            "4e755b56-3bd6-4da2-897a-d6de654881c1": {
              "id": "4e755b56-3bd6-4da2-897a-d6de654881c1",
              "name": "Tracardi.com",
              "production": true,
              "running": true,
              "type": [
                "rest"
              ],
              "bridge": {
                "id": "778ded05-4ff3-4e08-9a86-72c0195fa95d",
                "name": "REST API Bridge"
              },
              "timestamp": "2024-01-16T16:20:18",
              "description": "Collector to Tracardi.com web page",
              "channel": "Webpage",
              "enabled": true,
              "transitional": false,
              "tags": [
                "rest",
                "api"
              ],
              "groups": [],
              "permanent_profile_id": false,
              "requires_consent": false,
              "manual": null,
              "locked": true,
              "synchronize_profiles": true,
              "config": {
              }
            }
          }
        resources: |-
          {
            "resource_id_1": {
              "id": "resource_id_1",
              // Configuration
              "locked": true
            }
          }
        destinations: |-
          {
            "destination_id_1": {
              "id": "destination_id_1",
              // Configuration
              "locked": true
            }
          }
    ```

2. **Explanation:**
    - **config.preConfiguration:** Contains the JSON configuration for event sources, resources, and destinations.
    - **eventSources:** JSON object defining the event sources. Each event source must have a unique key (ID) and its configuration.
    - **resources:** JSON object defining the resources. Each resource must have a unique key (ID) and its configuration.
    - **destinations:** JSON object defining the destinations. Each destination must have a unique key (ID) and its configuration.
    - **locked:** Attribute must be set to `true` to ensure the configuration cannot be modified post-deployment.
