# Start Percona ClusterSync for MongoDB

Start {{pcsm.full_name}}.

=== ":material-console: Using `systemd`"

    We recommend to use the packaged service scripts to run `pcsm`.
    
    ```{.bash data-prompt="$"}
    $ sudo systemctl start pcsm
    ```

    Check the status with this command:

    ```{.bash data-prompt="$"}
    $ sudo systemctl status pcsm
    ```

=== ":fontawesome-solid-user-gear: Manually"

    You can start PCSM manually. This option is the way you start {{pcsm.full_name}} if you installed it [from source code](source.md) 

    Run Percona ClusterSync for MongoDB with the following command **if you haven't defined MongoDB connection string URI before**:

    ```{.bash data-prompt="$"}
    $ nohup pcsm --source <source-mongodb-uri> --target <target-mongodb-uri> --log-no-color > percona-clustersync-mongodb.log 2>&1 &
    ```

    Alternatively, you can use environment variables:

    ```{.bash data-prompt="$"}
    $ export SOURCE_URI=<source-mongodb-uri>
    $ export TARGET_URI=<target-mongodb-uri>
    $ nohup pcsm --log-no-color > percona-clustersync-mongodb.log 2>&1 &
    ```

See [Percona ClusterSync for MongoDB startup configuration](parameters.md) for all available options.

## Configure the HTTP listen address

By default, the PCSM HTTP server listens on localhost. The `--port option `controls the HTTP port.

This default keeps the PCSM control API and profiling endpoints accessible only from the local host.

In Kubernetes, HTTP liveness and readiness probes connect to the pod IP. To make the PCSM HTTP server reachable through the pod IP, set the listen host to `0.0.0.0:`

```text
$ PCSM_LISTEN_HOST=0.0.0.0 pcsm
```

Alternatively, use the `--listen-host` option:

$ pcsm --listen-host 0.0.0.0

The default value is localhost. You can also specify an IP address or DNS name. For example, to listen on the IPv6 loopback address:

```text
$ pcsm --listen-host ::1
```

Specify only the host with `--listen-host`. Do not include a port. `Use --port` to configure the HTTP port.

!!! warning

    Setting `--listen-host` to `0.0.0.0` makes the PCSM control API and profiling endpoints reachable through the network interfaces of the host or pod. These endpoints don't require authentication.

    In Kubernetes, use a `NetworkPolicy` or other network controls to restrict access. If you don't need to expose the HTTP endpoint on the pod network, you can use an exec-based health probe against `localhost` instead.

## How to see {{pcsm.full_name}} logs

With the packaged `systemd` service, the log output to `stdout` is captured by
systemd's default redirection to `systemd-journald`. You can view it with this
command:

```{.bash data-prompt="$"}
$ sudo journalctl -u pcsm.service
```

See `man journalctl` for useful options such as `--lines`, `--follow`, etc.


If you started `pcsm` manually, see the file you redirected `stdout` and `stderr` to.


## Next steps

Congratulations! you have successfully installed and connected PCSM to your source and target MongoDB. Now you have it up and running and you are ready to use it.

[Use {{pcsm.full_name}} :material-arrow-right:](usage.md){.md-button}