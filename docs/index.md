# {{plm.full_name}} documentation

!!! note ""

    This is the documentation for the latest release, **{{plm.short}} {{release}}** ([Release Notes](release-notes/{{release}}.md)).


--8<-- "plm-description.md"

[Get started :material-arrow-right:](installation.md){.md-button}
[How {{plm.full_name}} works :material-arrow-right:](intro.md){.md-button}

## Features

* **Data clone**: Transfer existing data from a source MongoDB to a target MongoDB deployment.
* **Real-time replication**: {{plm.full_name}} uses MongoDB [change streams :octicons-link-external-16:](https://mongodb.com/docs/manual/changeStreams/) to track changes in your source cluster and replicate them to target in real time.
* **Namespace filtering**: Specify which databases and collections to include or exclude.
* **Automatic index management**: Ensure necessary indexes are created on the target.
* **HTTP API**: Start, finalize, pause, resume, and check replication status via HTTP endpoints.

## Why you need PLM

Benefit from {{plm.full_name}} in the following use cases:

* **Disaster recovery**:

    {{plm.short}} enables you to maintain a secondary cluster as a backup. In case of a failure in the primary cluster, the secondary cluster can take over, ensuring minimal downtime.
    
* **Data migration**:

    {{plm.short}} simplifies the process of migrating data between clusters, whether you're upgrading to a new MongoDB version, moving to a different vendor, or transitioning from cloud to on-premises.

* **Global data distribution**

    Synchronize data across geographically distributed clusters to improve data access speed and reduce latency for users in different regions.

* **Testing and development**:

    Keep a test or development cluster in sync with the production cluster to ensure accurate testing and debugging without affecting live data.

* **Hybrid cloud deployments**

    Synchronize data between on-premises clusters and cloud clusters, enabling hybrid cloud strategies.
