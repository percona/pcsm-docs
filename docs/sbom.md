# Software Bill of Materials

A Software Bill of Materials (SBOM) is a machine-readable inventory of the components and dependencies included in a software release. It helps you understand what is included in a build and assess potential security or compliance risks.

Starting with version 0.9.0, every Percona ClusterSync for MongoDB (PCSM) release includes a [CycloneDX 1.6 :octicons-link-external-16:](https://cyclonedx.org/specification/overview/){:target="_blank"} SBOM in JSON format.

## Why it matters

An SBOM can help you:

- Identify the components and dependencies included in a PCSM release.
- Assess known vulnerabilities using SBOM-compatible security scanners.
- Support compliance, audit, and software supply chain requirements.

## Where to find the SBOM

| Distribution method | SBOM location |
|---|---|
| Binary tarball | `<product>-<version>/<product>-<version>.cdx.json` inside the archive |
| RPM package | `/usr/share/doc/percona-clustersync-mongodb/percona-clustersync-mongodb-<version>.cdx.json` |
| DEB package | `/usr/share/doc/percona-clustersync-mongodb/percona-clustersync-mongodb-<version>.cdx.json` |
| Docker image | Two SBOMs ship together — see [Docker images](#docker-images) below |

## Verifying and scanning the SBOM

All examples below use [Trivy](https://trivy.dev/). [Grype](https://github.com/anchore/grype), Snyk, and any other CycloneDX-compatible scanner work the same way.

### Binary tarball

```bash
# Confirm the SBOM is bundled
tar tzf percona-clustersync-mongodb-0.9.0-x86_64.tar.gz | grep cdx.json

# Extract and scan
tar xzf percona-clustersync-mongodb-0.9.0-x86_64.tar.gz \
    -C /tmp percona-clustersync-mongodb-0.9.0/percona-clustersync-mongodb-0.9.0.cdx.json
trivy sbom --severity HIGH,CRITICAL --ignore-unfixed \
    /tmp/percona-clustersync-mongodb-0.9.0/percona-clustersync-mongodb-0.9.0.cdx.json
```

### RPM package

```bash
# Confirm the package installs the SBOM
rpm -ql percona-clustersync-mongodb | grep cdx.json

# Scan it (replace 9.x with your RHEL/OL version)
trivy sbom --severity HIGH,CRITICAL --ignore-unfixed --distro redhat/9.x \
    /usr/share/doc/percona-clustersync-mongodb/percona-clustersync-mongodb-0.9.0.cdx.json
```

### DEB package

```bash
# Confirm the package installs the SBOM
dpkg -L percona-clustersync-mongodb | grep cdx.json

# Scan it
trivy sbom --severity HIGH,CRITICAL --ignore-unfixed \
    /usr/share/doc/percona-clustersync-mongodb/percona-clustersync-mongodb-0.9.0.cdx.json
```

### Docker images

Each PCSM Docker image (DockerHub `percona/percona-clustersync-mongodb`, PerconaLab `perconalab/percona-clustersync-mongodb`) ships with **two** CycloneDX 1.6 SBOMs that describe overlapping scopes:

| SBOM | Scope | How to access |
|---|---|---|
| **Embedded** | PCSM binary + Go modules only | Inside the image filesystem |
| **OCI-attached** | Full image — PCSM + UBI9 base OS packages | Registry-side, via the OCI Referrers API |

**Easiest path** — `trivy image --sbom-sources oci` fetches the attached SBOM via the OCI Referrers API and scans it, without pulling the image:

```bash
trivy image --severity HIGH,CRITICAL --ignore-unfixed --sbom-sources oci \
    docker.io/percona/percona-clustersync-mongodb:0.9.0
```

**Embedded SBOM** — same as in the RPM, just inside the image:

```bash
docker run --rm -it --entrypoint cat \
    docker.io/percona/percona-clustersync-mongodb:0.9.0 \
    /usr/share/doc/percona-clustersync-mongodb/percona-clustersync-mongodb-0.9.0.cdx.json \
    | trivy sbom --severity HIGH,CRITICAL --ignore-unfixed -
```

**Manual inspection** with the [ORAS CLI](https://oras.land/):

```bash
# Use the per-arch tag - it resolves directly to the image manifest
oras discover --format tree \
    docker.io/percona/percona-clustersync-mongodb:0.9.0-amd64

# Then pull the SBOM referrer (use the digest from the discover output)
oras pull docker.io/percona/percona-clustersync-mongodb@sha256:<referrer-digest>
```