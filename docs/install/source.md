# Build from source code

## Before you start

Check the [system requirements](../system-requirements.md)  and [known limitations](../limitations.md).

## Prerequisites

To build {{pcsm.full_name}} from source, you need the following:

- Go 1.24 or later. [Install and set up Go tools :octicons-link-external-16:](https://golang.org/doc/install)x
- make
- git

## Build steps

Here's how to build {{pcsm.full_name}}:
{.power-number}

1. Clone the repository and change directory to `pcsm`:

    ```bash
    git clone https://github.com/percona/percona-link-mongodb.git
    cd pcsm
    ```

2. Build the project using the Makefile:

    ```bash
    make build
    ```

    Alternatively, you can install {{pcsm.short}} from the cloned repo using `go install`:

    ```bash
    go install .
    ```

    This installs `pcsm` into your `GOBIN` directory. 

3. Add `GOBIN` to your `PATH`. This makes `pcsm` a global command in your terminal.

## Next steps

[Configure authentication :material-arrow-right:](authentication.md){.md-button}