# Install {{plm.full_name}} from Percona repositories

To install the software from Percona repositories means to subscribe to them. Percona provides the [`percona-release` :octicons-link-external-16:](https://www.percona.com/doc/percona-repo-config/index.html) repository management tool. It automatically enables the required repository so that you can install and update both {{plm.full_name}} packages and required dependencies smoothly.

## Supported operating systems

{{plm.full_name}} is available on the following operating systems:

* Debian 11
* Debian 12
* Ubuntu 20.04 (Focal Fossa)
* Ubuntu 22.04 (Jammy Jellyfish)
* Ubuntu 24.04 (Noble Numbat)
* Red Hat Enterprise Linux and compatible derivatives 8 and 9
* Amazon Linux 2023

## Before you start

Check the [system requirements](../system-requirements.md) and [known limitations](../limitations.md).

Data migration is a resource-intensive task. Therefore, we recommend installing PLM on the instance closest to the target to reduce the network lag as much as possible.s

## Procedure

<i warning>:material-alert: Warning:</i> Run the following commands as root or via the `sudo` command.

=== ":material-debian: On Debian and Ubuntu" 

    1. Install `percona-release`:

        --8<-- "percona-release-apt.md"

    2. Enable the repository    

        ```{.bash data-prompt="$"}
        $ sudo percona-release enable plm release
        ```

    3. Install the package:

        ```{.bash data-prompt="$"}
        $ sudo apt install percona-link-mongodb
        ```

=== ":material-redhat: On RHEL and derivatives" 

    1. Install `percona-release`:

        --8<-- "percona-release-yum.md"

    2. Enable the repository    

        ```{.bash data-prompt="$"}
        $ sudo percona-release enable plm release
        ```  

    3. Install the package:

        ```{.bash data-prompt="$"}
        $ sudo yum install percona-link-mongodb
        ``` 

=== ":fontawesome-brands-amazon: On Amazon Linux 2023" 

    1. Install `percona-release`:

        --8<-- "percona-release-yum.md"

    2. Enable the repository    

        ```{.bash data-prompt="$"}
        $ sudo percona-release enable plm release
        ```  

    3. Install the package:

        ```{.bash data-prompt="$"}
        $ sudo yum install percona-link-mongodb
        ``` 
    
Congratulations! You have successfully installed {{plm.full_name}}. Now you must connect it to source and target MongoDB deployments.

## Next steps

[Configure authentication :material-arrow-right:](authentication.md){.md-button}
