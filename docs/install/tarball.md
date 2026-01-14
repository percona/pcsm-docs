# Download {{pcsm.full_name}} from Percona website

You can download {{pcsm.full_name}} from [Percona website :octicons-link-external-16:](https://www.percona.com/downloads/percona-clustersync-mongodb/) and install it:

* [From binary tarballs](#install-from-binary-tarballs). Tarballs only for x86_64 architecture are available.
* Manually, from the installation packages using `dpkg` (Debian and Ubuntu) or `rpm` (Red Hat Enterprise Linux and derivative). However, you must make sure that all dependencies are satisfied.


## Before you start

Check the [system requirements](../system-requirements.md) and [supported MongoDB versions](../deployment.md).

## Install from binary tarballs

Find the link to the binary tarballs under the **Generic Linux** menu item on [Percona website :octicons-link-external-16:](https://www.percona.com/downloads/percona-clustersync-mongodb/).
{.power-number}

1. Fetch the binary tarball. Replace the version in the URL with your required version.

    ```bash
    wget https://downloads.percona.com/downloads/percona-clustersync-mongodb/percona-clustersync-mongodb-{{release}}/binary/tarball/percona-clustersync-mongodb-{{release}}-x86_64.tar.gz
    ```

2. Extract the tarball

    ```bash
    tar -xf percona-clustersync-mongodb-{{release}}-x86_64.tar.gz
    ```

3. Export the location of the binaries to the `PATH` variable

    For example, if you’ve extracted the tarball to your `home` directory, the command would be the following:

    ```bash
    export PATH=~/percona-clustersync-mongodb-{{release}}/:$PATH
    ```

## Next steps

[Configure authentication :material-arrow-right:](authentication.md){.md-button}
