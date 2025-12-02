# Configure authentication in MongoDB

{{plm.full_name}} uses the authentication and authorization subsystem of MongoDB. This means that to authenticate {{plm.full_name}}, you need to:

* [Create users in source and target cluster](#create-users)
* [Set a valid MongoDB connection string URI for source and target cluster](#set-mongodb-connection-string-uri)

## Create users

You need to create users in both source and target clusters. You will use these user credentials to create the MongoDB connection string URI.
{.power-number}

1. Connect to the **source** cluster and run the following command:

    ```javascript
    db.getSiblingDB('admin').createUser({
      user: 'source',
      pwd: 'mys3cretpAss',
      roles: ['backup', 'clusterMonitor',  'readAnyDatabase'],
    });
    ```

2. Connect to the **target** cluster and run the following command:

    ```javascript
    db.getSiblingDB('admin').createUser({
       user: 'target',
       pwd: 'tops3cr3t',
       roles: ['restore', 'clusterMonitor', 'clusterManager',       'readWriteAnyDatabase'],
      });
    ```

## Set MongoDB connection string URI

{{plm.full_name}} authenticates in source and target clusters using the MongoDB Connection string URI. It has the following format:

```
mongodb://user:pwd@host1:port1,host2:port2,host3:port3/[authdb]?[options]
```

To connect PLM to source and target MongoDB clusters, specify the MongoDB Connection string URI for the `PLM_SOURCE_URI` and `PLM_TARGET_URI` environment variables in its environment file. 

When you [install PLM from repositories](repos.md), the environment file is created for you. You can find it at the following path:

* for Debian and Ubuntu: `/etc/default/plm`
* for RHEL and derivatives: `/etc/sysconfig/plm`

### Example environment file 

```{.text .no-copy}
PLM_SOURCE_URI="mongodb://source:mys3cretpAssword@mysource1:27017,mysource2:27017,mysource3:27017/"
PLM_TARGET_URI="mongodb://target:tops3cr3t@mytarget1:27017,mytarget2:27017,mytarget3:27017/"
```

### Passwords with special characters

If the password includes special characters like `#`, `@`, `/` and so on, you must convert these characters using the [percent-encoding mechanism](https://datatracker.ietf.org/doc/html/rfc3986#section-2.1) when passing them to Percona Link for MongoDB. For example, the password `secret#pwd` should be passed as `secret%23pwd`.

### MongoDB connection string options

You can pass additional connection options to the MongoDB connection string. The string of options begins with the question mark (`?`).

{{plm.full_name}} accepts the following authentication and TLS-related options:

| Option | Description |
|--------|-------------|
| `appName` | Specifies the name of the application that is connecting to MongoDB. This name appears in the MongoDB logs and can be useful for identifying the source of connections. |
| `replicaSet` | Specifies the name of the replica set if a `mongod` is a member of it. |
| `authSource` | Specifies the database that contains the user's credentials. Defaults to the database specified in the connection string. If not specified, defaults to the `admin` database|
| `authMechanism` | Specifies the authentication mechanism to use. Common values include: SCRAM-SHA-1, SCRAM-SHA-256, MONGODB-X509, GSSAPI, PLAIN, and MONGODB-AWS. |
| `authMechanismProperties` | Specifies additional properties for the authentication mechanism. Format is `key=value` pairs separated by commas. |
| `gssapiServiceName` | Specifies the service name to use for GSSAPI authentication. Defaults to "mongodb". |
| `tls` | Enables TLS/SSL for the connection. Use this option instead of the deprecated `ssl` option. |
| `ssl` | (Deprecated) Enables SSL for the connection. Use `tls` instead. |
| `tlsCertificateKeyFile` | Specifies the path to the client certificate and private key file for TLS/SSL connections. |
| `tlsCertificateKeyFilePassword` | Specifies the password for the client certificate key file if it is encrypted. |
| `tlsCAFile` | Specifies the path to the CA certificate file for TLS/SSL connections. |
| `tlsAllowInvalidCertificates` | Allows connections to servers with invalid certificates. Not recommended for production use. |
| `tlsAllowInvalidHostnames` | Allows connections to servers with invalid hostnames. Not recommended for production use. |
| `tlsInsecure` | Disables certificate validation. Not recommended for production use. |

## Next steps 

[Start PLM :material-arrow-right: ](start-plm.md){.md-button}