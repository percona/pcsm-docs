# {{plm.full_name}} deployment architecture

Percona ClusterSync for MongoDB (PCSM) is a middleware synchronization tool that connects source and target clusters. It reads change streams from the source cluster and applies those changes to the target cluster. 

Since PCSM operates as a standalone binary process, its placement within your infrastructure can significantly impact performance, especially regarding network latency, which can affect replication time. 

You can deploy PCSM using one of three different architectures.


## Dedicated host (intermediary)

The PCSM process runs on a dedicated machine, which can be a virtual machine, container, or physical server. This machine is logically placed between the source and target clusters. Since data migration is resource-intensive, its recommended to install PCSM as close to the target cluster as possible to reduce network latency.

!!! info "Recommended deployment"
    This deployment architecture is recommended for Production as it is the most robust and safe architecture for critical data synchronization.


![Dedicated host](_images/pcsm_dedicated_host.png)


| Pros | Cons |
|------|------|
| **Resource isolation**: PCSM has its own dedicated CPU and RAM, ensuring it does not **starve** the source or target databases.
| **Network latency**: Adds an extra network hop (Source → PCSM → Target), introducing some latency, which is typically negligible in modern, low-latency networks. |
| **Stability**: In the event that PCSM crashes or becomes unresponsive, both the source and target clusters will remain completely unaffected.| **Infrastructure cost**: Requires provisioning and maintaining an additional compute resource for the PCSM service. |
| **Scalability**: The PCSM host can be vertically scaled (for example, adding memory for large in-memory buffers) without modifying database hardware. |  |


## Target node (Co-located)

The PCSM process runs directly on a primary node in the target cluster.


!!! info "Recommended deployment"
    This deployment architecture is recommended for **one-way migrations** where the target cluster is currently empty and not serving application traffic.


![Target node](_images/pcsm_target_node_deployment.png)

| Pros | Cons |
|------|------|
| **Efficient writes:**  Write operations are applied locally to the target, reducing write latency. |Vertical scalability also impact the database |
| **Safer for Production:**: Resource contention (CPU/RAM spikes) occurs on the target cluster, leaving the production source cluster unaffected. |
