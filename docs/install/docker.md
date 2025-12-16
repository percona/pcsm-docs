# Run {{pcsm.full_name}} in Docker

You can run {{pcsm.full_name}} as a Docker container. This is useful for such use cases:

* you want to try out {{pcsm.full_name}} quickly without complex setup
* your MongoDB clusters also run in Docker 
* you want to isolate {{pcsm.full_name}} in a containerized environment.

Docker images of {{pcsm.full_name}} are hosted publicly on [Docker Hub :octicons-link-external-16:](https://hub.docker.com/r/perconalab/percona-clustersync-mongodb).

For more information about using Docker, see the [Docker Docs :octicons-link-external-16:](https://docs.docker.com/).

Make sure that you are using the latest version of Docker. The ones provided via apt and yum may be outdated and cause errors.

By default, Docker will pull the image from Docker Hub if it is not available locally.

## Prerequisites

1. You need to either deploy MongoDB or Percona Server for MongoDB as your source and target clusters or use existing deployments. Both clusters can run in Docker containers, on virtual machines, or in cloud environments. 

2. The {{pcsm.short}} container must be able to reach all nodes in both source and target MongoDB clusters over the network. This includes:

    * All replica set members that can become primary
    * The `mongos` nodes in source and target clusters 

3. Create users in both source and target clusters with appropriate permissions for authentication. 

    For example, to create a user for {{pcsm.short}} in Percona Server for MongoDB running in Docker, use the following command, replacing `psmdb` with your container name, `source` with the username and `mys3cretpAss` with the password:

    ```bash
    docker exec -it psmdb mongosh --eval '
    db.getSiblingDB("admin").createUser({
      user: "source",
      pwd: "mys3cretpAss",
      roles: ["backup", "clusterMonitor", "readAnyDatabase"]
    });'
    ```

    See [Configure authentication](authentication.md) for details.

4. Your source cluster has some data to verify the replication.

## Deploy source and target clusters

In this example configuration we spin up single-node replica sets in Docker containers named `psmdb-source` and `psmdb-target`, respectively.

In production, use the minimum recommended [three member replica sets](https://www.mongodb.com/docs/manual/core/replica-set-architecture-three-members/).

If you already have source and target clusters deployed, skip this step.

1. Create a Docker network:

    ```{.bash data-prompt="$"}
    $ docker network create mymongo
    ```

2. Start Percona Server for MongoDB containers

    * Start the container for the source replica set:

       ```bash
       docker run -d \
         --name psmdb-source \
         --net mymongo \
         -p 27017:27017 \
         percona/percona-server-mongodb:8.0 \
         mongod --replSet rs1 --bind_ip_all
       ```

    * Start the container for the target replica set and map a different port:

       ```bash
       docker run -d \
         --name psmdb-target \
         --net mymongo \
         -p 27018:27017 \
         percona/percona-server-mongodb:8.0 \
         mongod --replSet rs2 --bind_ip_all
       ```    

2. Initialize replica sets:

    For the source:

    ```bash
    docker exec -it psmdb-source mongosh --eval 'rs.initiate({
      _id: "rs1",
      members: [{ _id: 0, host: "psmdb-source:27017" }]
    })'
    ```

    For the target:

    ```bash
    docker exec -it psmdb-target mongosh --eval 'rs.initiate({
      _id: "rs2",
      members: [{ _id: 0, host: "psmdb-target:27017" }]
    })'
    ```

3. Verify that your replica sets are initialized and running:

    ```{.bash data-prompt="$"}
    docker exec -it psmdb-source mongosh --eval 'rs.status()'
    docker exec -it psmdb-target mongosh --eval 'rs.status()'
    ```

4. Create a user for {{pcsm.full_name}} on the source:

    ```bash
    docker exec -it psmdb-source mongosh --eval '
    db.getSiblingDB("admin").createUser({
      user: "source",
      pwd: "mys3cretpAss",
      roles: ["backup", "clusterMonitor", "readAnyDatabase"]
    });'
    ```

5. Create a user for {{pcsm.full_name}} on the target:

    ```bash
    docker exec -it psmdb-target mongosh --eval '
    db.getSiblingDB("admin").createUser({
      user: "target",
      pwd: "t0ps3cret",
      roles: ["backup", "clusterMonitor", "readAnyDatabase"]
    });'
    ```

## Start {{pcsm.full_name}} 

Start the {{pcsm.short}} container. You can specify connection strings using environment variables or command-line flags:

=== "Environment variables"

    Use the `PCSM_SOURCE_URI` and `PCSM_TARGET_URI` environment variables:

    ```{.bash data-prompt="$"}
    $ docker run --name pcsm1 --network mymongo -d \
        -e PCSM_SOURCE_URI="mongodb://<source-user>:<source-password>@psmdb-source:27017" \
        -e PCSM_TARGET_URI="mongodb://<target-user>:<target-password>@psmdb-target:27017" \
        perconalab/percona-clustersync-mongodb:latest
    ```

    Replace `<source-user>:<source-password>` and `<target-user>:<target-password>` with the credentials of the users you created for `pcsm` process in the source and target clusters.

=== "Command-line flags"

    Pass the `--source` and `--target` flags directly:

    ```{.bash data-prompt="$"}
    $ docker run --name pcsm1 --network mymongo -d \
        perconalab/percona-clustersync-mongodb:latest \
        --source "mongodb://<source-user>:<source-password>@psmdb-source:27017" \
        --target "mongodb://<target-user>:<target-password>@psmdb-target:27017"
    ```

    Replace `<source-user>:<source-password>` and `<target-user>:<target-password>` with the credentials of the users you created for `pcsm` process in the source and target clusters.

??? tip "Additional options"

    You can combine environment variables with command-line flags or add other options:

    ```{.bash data-prompt="$"}
    $ docker run --name pcsm1 --network mymongo -d \
        -e PCSM_SOURCE_URI="mongodb://source:password@psmdb-source:27017" \
        -e PCSM_TARGET_URI="mongodb://target:password@psmdb-target:27017" \
        -p 2242:2242 \
        perconalab/percona-clustersync-mongodb:latest \
        --port 2242 \
        --log-level debug
    ```

    See [startup configuration](parameters.md) for all available options.

2. Check the initial status of {{pcsm.short}}:

    ```{.bash data-prompt="$"}
    $ docker exec -it pcsm1 pcsm status
    ```

    The status should be `idle`, indicating {{pcsm.short}} is ready to accept requests.


## Run {{pcsm.short}}

1. Start the replication process:

    ```bash
    docker exec -it pcsm1 pcsm start
    ```

2. Monitor replication by checking the status:

    ``bash
    docker exec -it pcsm1 pcsm status
    ```

3. View logs to monitor activity:

    ```{.bash data-prompt="$"}
    $ docker logs -f pcsm1
    ```


## Next steps

[Use {{pcsm.full_name}} :material-arrow-right:](usage.md){.md-button}
