# Migrate Persistent Query Settings

Percona ClusterSync for MongoDB doesn't automatically migrate [Persistent Query 
Settings (PQS)](reference/glossary.md#persistent-query-settings). If you have Persistent Query 
Settings defined on your source cluster, you must manually migrate them from the source to the target cluster after the replication is complete and you have [finalized](install/usage.md#finalize-the-replication) it. With this post-migration step you ensure consistent query performance.

!!! note "For source and target clusters of version 8.0 and above"

    The procedure in this document applies only to source and target clusters running MongoDB version 8.0 and above, as persistent query settings were introduced starting with MongoDB 8.0.

Use the following procedure to manually migrate your [Persistent Query Settings](reference/glossary.md#persistent-query-settings) to the destination cluster:

You'll need to:

1. [Export Persistent Query Settings from the source cluster](#export-persistent-query-settings-from-the-source-cluster)
2. [Import Persistent Query Settings to the destination cluster](#import-persistent-query-settings-to-the-destination-cluster)

## Export Persistent Query Settings from the source cluster

1. Connect to your source cluster using `mongosh` and run the following command. This command uses the `$querySettings` aggregation stage to retrieve all defined query settings and outputs them as a JSON array to the console.

    ```javascript
    db.aggregate([{ $querySettings: {} }])
    ```

2. Copy the output array. You will use this data in the next step. If an array is empty, it means that you have not defined any query settings.

    The output will look similar to this structure:

    ```json
    [
      {
        queryShapeHash: '7EF99ED4856D6DDF6224F8A728E553ECF016C9D1520BF921277A5D2B6618D125',
        representativeQuery: {
          find: 'products',
          filter: { category: 'example' },
          '$db': 'inventoryDB'
        },
        settings: {
          indexHints: [
            {
              ns: { db: 'inventoryDB', coll: 'products' },
              allowedIndexes: [ 'category_index' ]
            }
          ]
        }
      }
    ]
    ```

## Import Persistent Query Settings to the destination cluster

For each query setting object you exported from the source, run a command on the destination cluster to apply it. Percona Server for MongoDB uses the `setQuerySettings` command for this purpose.

The key to identifying the query shape depends on the fields available in your exported setting:

* If the query setting includes a `representativeQuery` field, use the value of that field to identify the query.
* Otherwise, use the `queryShapeHash` field value.

Connect to your destination cluster using `mongosh` and execute the appropriate command for each setting you wish to migrate.

**Example using `representativeQuery`:**

Based on the first object in the example array above, you would run:

```javascript
db.adminCommand({
  setQuerySettings: {
    find: "products",
    filter: { category: "example" }, 
    $db: "inventoryDB"
  },
  settings: {
    indexHints: {
      ns: { db: "inventoryDB", coll: "products" },
      allowedIndexes: [ "category_index" ]
    }
  }
})
```

**Example using `queryShapeHash`:**

Based on the second object in the example array, which lacks a `representativeQuery`, you would run:

```javascript 
db.adminCommand({
   setQuerySettings: { queryShapeHash: "A19F4D5C" },
   settings: {
      "comment": "Legacy reporting query, must not use a specific index."
   }
})
```

The above example assumes the `queryShapeHash` contains a valid value. After applying all the necessary query settings to your destination cluster, your queries will benefit from the same performance optimizations as they did on the source cluster. You can now safely complete the migration cutover process with Percona ClusterSync for MongoDB.
