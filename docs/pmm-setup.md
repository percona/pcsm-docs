# Set up observability with Percona Monitoring and Management

{{plm.full_name}} exports Prometheus metrics enabling you to monitor the replication performance including the number of processed events, data transfer sizes, document counts, and batch processing times. These metrics are available at the `/metrics` endpoint. 

[Available metrics](#available-metrics){.md-button}

You can use any monitoring tool of your choice to collect and analyze these metrics. We recommend and provide instructions for setting up observability with [Percona Monitoring and Management (PMM)](https://docs.percona.com/percona-monitoring-and-management/3/index.html).

{{plm.full_name}} is natively integrated with PMM for automated monitoring of replication performance with data visualization on dashboards. This comprehensive monitoring helps you optimize replication performance and quickly identify any potential issues during the replication process.

PMM is the server-client solution. The PMM Client collects the metrics and sends them to the PMM Server. PMM Server displays these metrics on dashboards in a user-friendly way.

PMM Server and PMM Client are installed separately. 

## Prerequisites

1. You must have PMM server up and running. You can run PMM Server as a Docker image, install it a virtual appliance, or on an AWS instance. Follow the [Quickstart quide :octicons-link-external-16:](https://docs.percona.com/percona-monitoring-and-management/3/quickstart/quickstart.html) to start PMM Server in a Docker container. For other installation options, see [PMM Documentation :octicons-link-external-16:](https://docs.percona.com/percona-monitoring-and-management/3/install-pmm/install-pmm-server/index.html)
2. Ensure PMM server and PLM can communicate with each other over the network.

## Install PMM Client

1. You must install PMM Client on the same instance where {{plm.full_name}} is running. Refer to the [installation instructions :octicons-link-external-16:](https://docs.percona.com/percona-monitoring-and-management/3/install-pmm/install-pmm-client/index.html) suitable for your deployment
2. Register the client node in PMM Server. Replace the `admin:admin` with your PMM Server credentials and the `X.X.X.X` with the PMM Server IP address in the following command:
   
    ```{.bash data-prompt="$"}
    $ pmm-admin config --server-insecure-tls --server-url=https://admin:admin@X.X.X.X:443
    ```
    
    ??? example "Expected output"

        ```{.text .no-copy}
        Registering pmm-agent on PMM Server...
        Registered.
        Configuration file /usr/local/percona/pmm/config/pmm-agent.yaml updated.
        Reloading pmm-agent configuration...
        Configuration reloaded.
        Checking local pmm-agent status...
        pmm-agent is running.
        ```

## Configure monitoring for PLM

To enable metrics collection, add PLM as an external service to PMM server, Run the following command:

```{.bash data-prompt="$"}
$ pmm-admin add external --service-name=plm_test --listen-port=2242 --metrics-path=metrics --scheme=http
```

??? example "Expected output"
 
    ```{.text .no-copy}
    External Service added.
    Service ID  : 0b3460d9-4173-4ff8-adcd-105883a4ef56
    Service name: plm_test
    Group       : external
    ```

Now PMM Client collects the metrics for PLM.

## Create a dashboard 

To view PLM metrics, configure a dashboard in PMM Server. Here's how:

1. Log in to PMM Server
2. From the main menu, select **Dashboards** and click **New**
3. Select **Import a dashboard**
4. Copy the following metrics file in the **Import via dashboard JSON model** window and click **Load**

    ??? admonition "PLM Metrics file"

        ```json
        {
          "annotations": {
            "list": [
              {
                "builtIn": 1,
                "datasource": {
                  "type": "grafana",
                  "uid": "-- Grafana --"
                },
                "enable": true,
                "hide": true,
                "iconColor": "rgba(0, 211, 255, 1)",
                "name": "Annotations & Alerts",
                "type": "dashboard"
              }
            ]
          },
          "editable": true,
          "fiscalYearStartMonth": 0,
          "graphTooltip": 0,
          "id": 75,
          "links": [],
          "panels": [
            {
              "datasource": {
                "type": "prometheus",
                "uid": "PA58DA793C7250F1B"
              },
              "description": "",
              "fieldConfig": {
                "defaults": {
                  "color": {
                    "mode": "palette-classic"
                  },
                  "custom": {
                    "axisBorderShow": false,
                    "axisCenteredZero": false,
                    "axisColorMode": "text",
                    "axisLabel": "",
                    "axisPlacement": "auto",
                    "barAlignment": 0,
                    "drawStyle": "line",
                    "fillOpacity": 0,
                    "gradientMode": "none",
                    "hideFrom": {
                      "legend": false,
                      "tooltip": false,
                      "viz": false
                    },
                    "insertNulls": false,
                    "lineInterpolation": "linear",
                    "lineWidth": 1,
                    "pointSize": 5,
                    "scaleDistribution": {
                      "type": "linear"
                    },
                    "showPoints": "auto",
                    "spanNulls": false,
                    "stacking": {
                      "group": "A",
                      "mode": "none"
                    },
                    "thresholdsStyle": {
                      "mode": "off"
                    }
                  },
                  "mappings": [],
                  "thresholds": {
                    "mode": "absolute",
                    "steps": [
                      {
                        "color": "green",
                        "value": null
                      },
                      {
                        "color": "red",
                        "value": 80
                      }
                    ]
                  },
                  "unit": "eps"
                },
                "overrides": []
              },
              "gridPos": {
                "h": 8,
                "w": 12,
                "x": 0,
                "y": 0
              },
              "id": 3,
              "options": {
                "legend": {
                  "calcs": [],
                  "displayMode": "list",
                  "placement": "bottom",
                  "showLegend": true
                },
                "tooltip": {
                  "mode": "single",
                  "sort": "none"
                }
              },
              "targets": [
                {
                  "datasource": {
                    "type": "prometheus",
                    "uid": "PA58DA793C7250F1B"
                  },
                  "disableTextWrap": false,
                  "editorMode": "code",
                  "expr": "rate(percona_link_mongodb_events_processed_total[1m])",
                  "fullMetaSearch": false,
                  "includeNullMetadata": true,
                  "instant": false,
                  "legendFormat": "Events Processed",
                  "range": true,
                  "refId": "A",
                  "useBackend": false
                }
              ],
              "title": "Events Processed Rate",
              "type": "timeseries"
            },
            {
              "datasource": {
                "type": "prometheus",
                "uid": "PA58DA793C7250F1B"
              },
              "fieldConfig": {
                "defaults": {
                  "color": {
                    "mode": "palette-classic"
                  },
                  "custom": {
                    "axisBorderShow": false,
                    "axisCenteredZero": false,
                    "axisColorMode": "text",
                    "axisLabel": "",
                    "axisPlacement": "auto",
                    "barAlignment": 0,
                    "drawStyle": "line",
                    "fillOpacity": 0,
                    "gradientMode": "none",
                    "hideFrom": {
                      "legend": false,
                      "tooltip": false,
                      "viz": false
                    },
                    "insertNulls": false,
                    "lineInterpolation": "linear",
                    "lineWidth": 1,
                    "pointSize": 5,
                    "scaleDistribution": {
                      "type": "linear"
                    },
                    "showPoints": "auto",
                    "spanNulls": false,
                    "stacking": {
                      "group": "A",
                      "mode": "none"
                    },
                    "thresholdsStyle": {
                      "mode": "off"
                    }
                  },
                  "mappings": [],
                  "thresholds": {
                    "mode": "absolute",
                    "steps": [
                      {
                        "color": "green",
                        "value": null
                      },
                      {
                        "color": "red",
                        "value": 80
                      }
                    ]
                  },
                  "unit": "s"
                },
                "overrides": []
              },
              "gridPos": {
                "h": 8,
                "w": 12,
                "x": 12,
                "y": 0
              },
              "id": 5,
              "options": {
                "legend": {
                  "calcs": [],
                  "displayMode": "list",
                  "placement": "bottom",
                  "showLegend": true
                },
                "tooltip": {
                  "mode": "single",
                  "sort": "none"
                }
              },
              "targets": [
                {
                  "datasource": {
                    "type": "prometheus",
                    "uid": "PA58DA793C7250F1B"
                  },
                  "editorMode": "code",
                  "expr": "percona_link_mongodb_lag_time_seconds",
                  "instant": false,
                  "legendFormat": "Lag Time",
                  "range": true,
                  "refId": "A"
                }
              ],
              "title": "Target Lag Time",
              "type": "timeseries"
            },
            {
              "collapsed": false,
              "gridPos": {
                "h": 1,
                "w": 24,
                "x": 0,
                "y": 8
              },
              "id": 4,
              "panels": [],
              "title": "Initial Sync",
              "type": "row"
            },
            {
              "datasource": {
                "type": "prometheus",
                "uid": "PA58DA793C7250F1B"
              },
              "fieldConfig": {
                "defaults": {
                  "color": {
                    "mode": "palette-classic"
                  },
                  "custom": {
                    "axisBorderShow": false,
                    "axisCenteredZero": false,
                    "axisColorMode": "text",
                    "axisLabel": "",
                    "axisPlacement": "auto",
                    "barAlignment": 0,
                    "drawStyle": "line",
                    "fillOpacity": 0,
                    "gradientMode": "none",
                    "hideFrom": {
                      "legend": false,
                      "tooltip": false,
                      "viz": false
                    },
                    "insertNulls": false,
                    "lineInterpolation": "linear",
                    "lineWidth": 1,
                    "pointSize": 5,
                    "scaleDistribution": {
                      "type": "linear"
                    },
                    "showPoints": "auto",
                    "spanNulls": false,
                    "stacking": {
                      "group": "A",
                      "mode": "none"
                    },
                    "thresholdsStyle": {
                      "mode": "off"
                    }
                  },
                  "mappings": [],
                  "thresholds": {
                    "mode": "absolute",
                    "steps": [
                      {
                        "color": "green",
                        "value": null
                      },
                      {
                        "color": "red",
                        "value": 80
                      }
                    ]
                  },
                  "unit": "decmbytes"
                },
                "overrides": []
              },
              "gridPos": {
                "h": 8,
                "w": 12,
                "x": 0,
                "y": 9
              },
              "id": 2,
              "options": {
                "legend": {
                  "calcs": [],
                  "displayMode": "list",
                  "placement": "bottom",
                  "showLegend": true
                },
                "tooltip": {
                  "mode": "single",
                  "sort": "none"
                }
              },
              "targets": [
                {
                  "datasource": {
                    "type": "prometheus",
                    "uid": "PA58DA793C7250F1B"
                  },
                  "disableTextWrap": false,
                  "editorMode": "code",
                  "expr": "percona_link_mongodb_copied_total_size_bytes_total / 1024 / 1024",
                  "fullMetaSearch": false,
                  "includeNullMetadata": true,
                  "instant": false,
                  "legendFormat": "Copied Size",
                  "range": true,
                  "refId": "A",
                  "useBackend": false
                },
                {
                  "datasource": {
                    "type": "prometheus",
                    "uid": "PA58DA793C7250F1B"
                  },
                  "editorMode": "code",
                  "expr": "percona_link_mongodb_estimated_total_size_bytes  / 1024 / 1024",
                  "hide": false,
                  "instant": false,
                  "legendFormat": "Estimated Total Size",
                  "range": true,
                  "refId": "B"
                }
              ],
              "title": "Cloned Size",
              "type": "timeseries"
            },
            {
              "datasource": {
                "type": "prometheus",
                "uid": "PA58DA793C7250F1B"
              },
              "fieldConfig": {
                "defaults": {
                  "color": {
                    "mode": "palette-classic"
                  },
                  "custom": {
                    "axisBorderShow": false,
                    "axisCenteredZero": false,
                    "axisColorMode": "text",
                    "axisLabel": "",
                    "axisPlacement": "auto",
                    "barAlignment": 0,
                    "drawStyle": "line",
                    "fillOpacity": 0,
                    "gradientMode": "none",
                    "hideFrom": {
                      "legend": false,
                      "tooltip": false,
                      "viz": false
                    },
                    "insertNulls": false,
                    "lineInterpolation": "linear",
                    "lineWidth": 1,
                    "pointSize": 5,
                    "scaleDistribution": {
                      "type": "linear"
                    },
                    "showPoints": "auto",
                    "spanNulls": false,
                    "stacking": {
                      "group": "A",
                      "mode": "none"
                    },
                    "thresholdsStyle": {
                      "mode": "off"
                    }
                  },
                  "mappings": [],
                  "thresholds": {
                    "mode": "absolute",
                    "steps": [
                      {
                        "color": "green",
                        "value": null
                      },
                      {
                        "color": "red",
                        "value": 80
                      }
                    ]
                  },
                  "unit": "s"
                },
                "overrides": []
              },
              "gridPos": {
                "h": 8,
                "w": 12,
                "x": 12,
                "y": 9
              },
              "id": 6,
              "options": {
                "legend": {
                  "calcs": [],
                  "displayMode": "list",
                  "placement": "bottom",
                  "showLegend": true
                },
                "tooltip": {
                  "mode": "single",
                  "sort": "none"
                }
              },
              "targets": [
                {
                  "datasource": {
                    "type": "prometheus",
                    "uid": "PA58DA793C7250F1B"
                  },
                  "editorMode": "code",
                  "expr": "percona_link_mongodb_initial_sync_lag_time_seconds",
                  "instant": false,
                  "legendFormat": "Lag time",
                  "range": true,
                  "refId": "A"
                }
              ],
              "title": "Initial Sync Lag Time",
              "type": "timeseries"
            },
            {
              "collapsed": false,
              "gridPos": {
                "h": 1,
                "w": 24,
                "x": 0,
                "y": 17
              },
              "id": 7,
              "panels": [],
              "title": "Process",
              "type": "row"
            },
            {
              "datasource": {
                "type": "prometheus",
                "uid": "PA58DA793C7250F1B"
              },
              "fieldConfig": {
                "defaults": {
                  "color": {
                    "mode": "palette-classic"
                  },
                  "custom": {
                    "axisBorderShow": false,
                    "axisCenteredZero": false,
                    "axisColorMode": "text",
                    "axisLabel": "",
                    "axisPlacement": "auto",
                    "barAlignment": 0,
                    "drawStyle": "line",
                    "fillOpacity": 0,
                    "gradientMode": "none",
                    "hideFrom": {
                      "legend": false,
                      "tooltip": false,
                      "viz": false
                    },
                    "insertNulls": false,
                    "lineInterpolation": "linear",
                    "lineWidth": 1,
                    "pointSize": 5,
                    "scaleDistribution": {
                      "type": "linear"
                    },
                    "showPoints": "auto",
                    "spanNulls": false,
                    "stacking": {
                      "group": "A",
                      "mode": "none"
                    },
                    "thresholdsStyle": {
                      "mode": "off"
                    }
                  },
                  "decimals": 0,
                  "mappings": [],
                  "thresholds": {
                    "mode": "absolute",
                    "steps": [
                      {
                        "color": "green",
                        "value": null
                      },
                      {
                        "color": "red",
                        "value": 80
                      }
                    ]
                  }
                },
                "overrides": [
                  {
                    "__systemRef": "hideSeriesFrom",
                    "matcher": {
                      "id": "byNames",
                      "options": {
                        "mode": "exclude",
                        "names": [
                          "plm"
                        ],
                        "prefix": "All except:",
                        "readOnly": true
                      }
                    },
                    "properties": [
                      {
                        "id": "custom.hideFrom",
                        "value": {
                          "legend": false,
                          "tooltip": false,
                          "viz": true
                        }
                      }
                    ]
                  }
                ]
              },
              "gridPos": {
                "h": 8,
                "w": 8,
                "x": 0,
                "y": 18
              },
              "id": 8,
              "options": {
                "legend": {
                  "calcs": [],
                  "displayMode": "list",
                  "placement": "bottom",
                  "showLegend": true
                },
                "tooltip": {
                  "mode": "single",
                  "sort": "none"
                }
              },
              "targets": [
                {
                  "datasource": {
                    "type": "prometheus",
                    "uid": "PA58DA793C7250F1B"
                  },
                  "editorMode": "code",
                  "exemplar": false,
                  "expr": "rate(round(go_goroutines{node_name=\"plm\"}[1m]))",
                  "instant": false,
                  "legendFormat": "{{node_name}}",
                  "range": true,
                  "refId": "A"
                }
              ],
              "title": "Running Goroutines",
              "type": "timeseries"
            },
            {
              "datasource": {
                "type": "prometheus",
                "uid": "PA58DA793C7250F1B"
              },
              "fieldConfig": {
                "defaults": {
                  "color": {
                    "mode": "palette-classic"
                  },
                  "custom": {
                    "axisBorderShow": false,
                    "axisCenteredZero": false,
                    "axisColorMode": "text",
                    "axisLabel": "",
                    "axisPlacement": "auto",
                    "barAlignment": 0,
                    "drawStyle": "line",
                    "fillOpacity": 0,
                    "gradientMode": "none",
                    "hideFrom": {
                      "legend": false,
                      "tooltip": false,
                      "viz": false
                    },
                    "insertNulls": false,
                    "lineInterpolation": "linear",
                    "lineWidth": 1,
                    "pointSize": 5,
                    "scaleDistribution": {
                      "type": "linear"
                    },
                    "showPoints": "auto",
                    "spanNulls": false,
                    "stacking": {
                      "group": "A",
                      "mode": "none"
                    },
                    "thresholdsStyle": {
                      "mode": "off"
                    }
                  },
                  "decimals": 0,
                  "mappings": [],
                  "thresholds": {
                    "mode": "absolute",
                    "steps": [
                      {
                        "color": "green",
                        "value": null
                      },
                      {
                        "color": "red",
                        "value": 80
                      }
                    ]
                  }
                },
                "overrides": [
                  {
                    "__systemRef": "hideSeriesFrom",
                    "matcher": {
                      "id": "byNames",
                      "options": {
                        "mode": "exclude",
                        "names": [
                          "plm"
                        ],
                        "prefix": "All except:",
                        "readOnly": true
                      }
                    },
                    "properties": [
                      {
                        "id": "custom.hideFrom",
                        "value": {
                          "legend": false,
                          "tooltip": false,
                          "viz": true
                        }
                      }
                    ]
                  }
                ]
              },
              "gridPos": {
                "h": 8,
                "w": 8,
                "x": 8,
                "y": 18
              },
              "id": 9,
              "options": {
                "legend": {
                  "calcs": [],
                  "displayMode": "list",
                  "placement": "bottom",
                  "showLegend": true
                },
                "tooltip": {
                  "mode": "single",
                  "sort": "none"
                }
              },
              "targets": [
                {
                  "datasource": {
                    "type": "prometheus",
                    "uid": "PA58DA793C7250F1B"
                  },
                  "editorMode": "code",
                  "exemplar": false,
                  "expr": "rate(round(go_threads{node_name=\"plm\"}[1m]))",
                  "instant": false,
                  "legendFormat": "{{node_name}}",
                  "range": true,
                  "refId": "A"
                }
              ],
              "title": "Running Threads",
              "type": "timeseries"
            },
            {
              "datasource": {
                "type": "prometheus",
                "uid": "PA58DA793C7250F1B"
              },
              "fieldConfig": {
                "defaults": {
                  "color": {
                    "mode": "palette-classic"
                  },
                  "custom": {
                    "axisBorderShow": false,
                    "axisCenteredZero": false,
                    "axisColorMode": "text",
                    "axisLabel": "",
                    "axisPlacement": "auto",
                    "barAlignment": 0,
                    "drawStyle": "line",
                    "fillOpacity": 0,
                    "gradientMode": "none",
                    "hideFrom": {
                      "legend": false,
                      "tooltip": false,
                      "viz": false
                    },
                    "insertNulls": false,
                    "lineInterpolation": "linear",
                    "lineWidth": 1,
                    "pointSize": 5,
                    "scaleDistribution": {
                      "type": "linear"
                    },
                    "showPoints": "auto",
                    "spanNulls": false,
                    "stacking": {
                      "group": "A",
                      "mode": "none"
                    },
                    "thresholdsStyle": {
                      "mode": "off"
                    }
                  },
                  "decimals": 0,
                  "mappings": [],
                  "thresholds": {
                    "mode": "absolute",
                    "steps": [
                      {
                        "color": "green",
                        "value": null
                      },
                      {
                        "color": "red",
                        "value": 80
                      }
                    ]
                  },
                  "unit": "decmbytes"
                },
                "overrides": [
                  {
                    "__systemRef": "hideSeriesFrom",
                    "matcher": {
                      "id": "byNames",
                      "options": {
                        "mode": "exclude",
                        "names": [
                          "plm"
                        ],
                        "prefix": "All except:",
                        "readOnly": true
                      }
                    },
                    "properties": [
                      {
                        "id": "custom.hideFrom",
                        "value": {
                          "legend": false,
                          "tooltip": false,
                          "viz": true
                        }
                      }
                    ]
                  }
                ]
              },
              "gridPos": {
                "h": 8,
                "w": 8,
                "x": 16,
                "y": 18
              },
              "id": 10,
              "options": {
                "legend": {
                  "calcs": [],
                  "displayMode": "list",
                  "placement": "bottom",
                  "showLegend": true
                },
                "tooltip": {
                  "mode": "single",
                  "sort": "none"
                }
              },
              "targets": [
                {
                  "datasource": {
                    "type": "prometheus",
                    "uid": "PA58DA793C7250F1B"
                  },
                  "editorMode": "code",
                  "exemplar": false,
                  "expr": "go_memstats_alloc_bytes{node_name=\"plm\"} / 1024 / 1024",
                  "instant": false,
                  "legendFormat": "{{node_name}}",
                  "range": true,
                  "refId": "A"
                }
              ],
              "title": "Memory",
              "type": "timeseries"
            }
          ],
          "refresh": "5s",
          "schemaVersion": 39,
          "tags": [],
          "templating": {
            "list": []
          },
          "time": {
            "from": "now-3m",
            "to": "now"
          },
          "timepicker": {},
          "timezone": "browser",
          "title": "Percona Link for MongoDB",
          "uid": "aegcuit193shse",
          "version": 8,
          "weekStart": ""
        }
        ```        
        
3. Verify the Dashboard details and click **Import**.

## Available metrics

You can collect and view the following PLM metrics at the `/metrics` endpoint:

| Metric name | Description |
|-------------|-------------|
| `percona_link_mongodb_events_processed_total` | Total number of events processed |
| `percona_link_mongodb_copy_read_size_bytes_total` | Total size of the read data in bytes |
| `percona_link_mongodb_copy_insert_size_bytes_total` | Total size of the inserted data in bytes |
| `percona_link_mongodb_lag_time_seconds` | Lag time in logical seconds between source and target clusters |
| `percona_link_mongodb_initial_sync_lag_time_seconds` | Lag time during the initial sync in seconds |
| `percona_link_mongodb_estimated_total_size_bytes` | Estimated total size of the data to be replicated in bytes |
| `percona_link_mongodb_copy_read_document_total` | Total count of the read documents |
| `percona_link_mongodb_copy_insert_document_total` | Total count of the inserted documents |
| `percona_link_mongodb_copy_read_batch_duration_seconds` | Read batch duration time in seconds |
| `percona_link_mongodb_copy_insert_batch_duration_seconds` | Insert batch duration time in seconds |
