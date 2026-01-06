# {{plm.full_name}} deployment architecture

Percona ClusterSync for MongoDB (PCSM) is a middleware synchronization tool that connects source and target clusters. It reads change streams from the source cluster and applies those changes to the target cluster. 

Since PCSM operates as a standalone binary process, its placement within your infrastructure can significantly impact performance, especially regarding network latency, which can affect replication time. 

You can deploy PCSM using one of three different architectures.


## Dedicated host (intermediary)

+-------------------+        +--------------------+        +-------------------+
|                   |        |                    |        |                   |
|  Source MongoDB   | -----> |        PCSM        | -----> |  Target MongoDB   |
|   Replica Set     |  read  |   Dedicated Host   | write  |     Cluster       |
|                   |        |                    |        |                   |
+-------------------+        +--------------------+        +-------------------+

