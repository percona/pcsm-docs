# Start Percona ClusterSync for MongoDB

Start {{pcsm.full_name}}.

=== ":material-console: Using `systemd`"

    We recommend to use the packaged service scripts to run `pcsm`.
    
    ```bash
    sudo systemctl start pcsm
    ```

    Check the status with this command:

    ```bash
    sudo systemctl status pcsm
    ```

=== ":fontawesome-solid-user-gear: Manually"

    You can start PCSM manually. This option is the way you start {{pcsm.full_name}} if you installed it [from source code](source.md) 

    Run Percona ClusterSync for MongoDB with the following command **if you haven't defined MongoDB connection string URI before**:

    ```bash
    nohup pcsm --source <source-mongodb-uri> --target <target-mongodb-uri> --no-color > percona-link-mongodb.log 2>&1 &
    ```

    Alternatively, you can use environment variables:

    ```bash
    export SOURCE_URI=<source-mongodb-uri>
    export TARGET_URI=<target-mongodb-uri>
    nohup pcsm --no-color > percona-link-mongodb.log 2>&1 &
    ```

See [Percona ClusterSync for MongoDB startup configuration](parameters.md) for all available options.


## How to see {{pcsm.full_name}} logs

With the packaged `systemd` service, the log output to `stdout` is captured by
systemd’s default redirection to `systemd-journald`. You can view it with this
command:

```bash
sudo journalctl -u pcsm.service
```

See `man journalctl` for useful options such as `--lines`, `--follow`, etc.


If you started `pcsm` manually, see the file you redirected `stdout` and `stderr` to.


## Next steps

Congratulations! you have successfully installed and connected PCSM to your source and target MongoDB. Now you have it up and running and you are ready to use it.

[Use {{pcsm.full_name}} :material-arrow-right:](usage.md){.md-button}