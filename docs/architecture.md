# {{plm.full_name}} deployment architecture

Percona ClusterSync for MongoDB (PCSM) is a middleware synchronization tool that connects source and target clusters. It reads change streams from the source cluster and applies those changes to the target cluster. 

Since PCSM operates as a standalone binary process, its placement within your infrastructure can significantly impact performance, especially regarding network latency, which can affect replication time. 

You can deploy PCSM using one of three different architectures.


## Dedicated host (intermediary)

The PCSM process runs on a dedicated machine, which can be a virtual machine, container, or physical server. This machine is logically placed between the source and target clusters. Since data migration is resource-intensive, its recommended to install PCSM as close to the target cluster as possible to reduce network latency.

!!! info "Recommendation"
    This deployment architecture is recommended for Production as it is the most robust and safe architecture for critical data synchronization.


![PLM states](_images/pcsm_dedicated_host.png)


| Pros | Cons |
|------|------|
| **Resource isolation**: PCSM runs with dedicated CPU and memory, preventing resource contention with the source or target MongoDB clusters. | **Network latency**: Adds an extra network hop (Source → PCSM → Target), introducing some latency, which is typically negligible in modern, low-latency networks. |
| **Stability**: PCSM crashes or restarts do not affect the availability or performance of either MongoDB cluster. | **Infrastructure cost**: Requires provisioning and maintaining an additional compute resource for the PCSM service. |
| **Scalability**: The PCSM host can be vertically scaled (for example, adding memory for large in-memory buffers) without modifying database hardware. |  |

