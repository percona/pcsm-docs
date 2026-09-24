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

By default, the PCSM HTTP server listens on `localhost`, which keeps the control API and the profiling endpoints reachable only from the local host. Most deployments don't need to change this.

Containerized deployments are the exception. Kubernetes runs HTTP liveness and readiness probes against the pod IP, and Docker forwards published ports to the container IP rather than the container loopback address. A loopback-only listener refuses these connections; failed readiness probes mark the pod unready, while repeated failed liveness probes can restart it.

## Set the bind host

To make the server reachable through the pod IP, set the listen host to `0.0.0.0` for an IPv4 pod or `::` for an IPv6 pod:

```{.bash data-prompt="$"}
$ PCSM_LISTEN_HOST=0.0.0.0 pcsm
```

For an IPv6 pod, use `::` instead:

```{.bash data-prompt="$"}
$ PCSM_LISTEN_HOST=:: pcsm
```

Alternatively, use the `--listen-host` option:

```{.bash data-prompt="$"}
$ pcsm --listen-host 0.0.0.0
```

For an IPv6 pod:

```{.bash data-prompt="$"}
$ pcsm --listen-host ::
```

You can also give an IP address or a DNS name. To listen on the IPv6 loopback address:

```{.bash data-prompt="$"}
$ pcsm --listen-host ::1
```

!!! warning
    Binding to `0.0.0.0` (IPv4) or :: (IPv6) exposes all PCSM HTTP endpoints on every network interface of the host or pod. This includes `/start`, `/pause`, `/resume`, `/finalize`, `/status`, `/metrics`, and the `pprof` profiling endpoints. None of them require authentication, so anything that can route to the pod can start, pause, or finalize replication.

    In Kubernetes, restrict access with a `NetworkPolicy` or an equivalent network control. If all you need is a health check, an exec probe against `localhost` gives you the same result with no network exposure.

### Accepted values

| **Value** | **Binds to** | **Use it for** |
| --- | --- | --- |
| `localhost` | `localhost:2242` | The default. Local host only. |
| `0.0.0.0` | `0.0.0.0:2242` | All IPv4 interfaces, including an IPv4 pod IP. |
| `::` | `[::]:2242` | All IPv6 interfaces, including an IPv6 pod IP. |
| An IP literal, such as `10.0.2.15` | `10.0.2.15:2242` | A single interface. |
| `::1` | `[::1]:2242` | The IPv6 loopback address. {{pcsm.short}} adds the brackets automatically. |
| A DNS name | Resolved when the server binds | A named interface. The name is accepted without being resolved first, so validation doesn't catch an unresolvable name. |
| Anything containing a port | Rejected at startup | Not supported. Values such as `localhost:2242`, `127.0.0.1:2242`, and `[::1]:2242` fail. Use `--port` to set the port. |

Changing the bind host doesn't affect the CLI. Subcommands such as `pcsm status` always connect to `localhost`. Keep the loopback address reachable or call the HTTP API directly at the address you configured. 

### What to pass

Give `--listen-host` a host and nothing else. The `--port` option sets the port, and defaults to `2242`.

A value that already contains a port is rejected, so `localhost:2242`, `127.0.0.1:2242`, and `[::1]:2242` all fail at startup. A DNS name is accepted without being resolved first, which means a name that can't be resolved isn't caught by validation.

Changing the bind host doesn't affect the CLI. Subcommands such as `pcsm status` always connect to `localhost`.

### Check that it worked

PCSM reports its bind address when the HTTP server starts. Read the startup log and confirm the address matches what you set:

```sh
INF s=http Starting HTTP server at http://0.0.0.0:2242
```

See [Percona ClusterSync for MongoDB startup configuration](parameters.md) for all available options, and [PCSM HTTP API](../api.md) for the endpoints themselves.

## How to see {{pcsm.full_name}} logs

With the packaged `systemd` service, the log output to `stdout` is captured by systemd's default redirection to `systemd-journald`. 

You can view it with this command:

```{.bash data-prompt="$"}
$ sudo journalctl -u pcsm.service
```

See `man journalctl` for useful options such as `--lines`, `--follow`, etc.


If you started `pcsm` manually, see the file you redirected `stdout` and `stderr` to.


## Next steps

Congratulations! you have successfully installed and connected PCSM to your source and target MongoDB. Now you have it up and running and you are ready to use it.

[Use {{pcsm.full_name}} :material-arrow-right:](usage.md){.md-button}