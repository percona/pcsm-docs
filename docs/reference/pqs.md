!!! note "Applies only to source and target clusters in version 8.0 and above."

# Migrate Persistent Query Settings

Use the following procedure to manually migrate your Persistent Query Settings to the destination cluster, ensuring consistent query performance post-migration.

## Steps

### 1. Export Persistent Query Settings from the source cluster

Connect to your source cluster using `mongosh` and run the following command. This command uses the `$querySettings` aggregation stage to retrieve all defined query settings and outputs them as a JSON array to the console.

```javascript
db.aggregate([{ $querySettings: {} }])
```

Copy the output array. You will use this data in the next step. If an array is empty, it means that you have not defined any query settings.

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

### 2. Import Persistent Query Settings to the Destination Cluster
For each query setting object you exported from the source, run a command on the destination cluster to apply it. Percona Server for MongoDB uses the `setQuerySettings` command for this purpose.

The key to identifying the query shape depends on the fields available in your exported setting:
* If the query setting includes a `representativeQuery` field, use the value of that field to identify the query.
* Otherwise, use the `queryShapeHash` field value.

Connect to your destination cluster using `mongosh` and execute the appropriate command for each setting you wish to migrate.

**Example using `representativeQuery`:**

Based on the first object in the example array above, you would run:

```JavaScript
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

```JavaScript
db.adminCommand({
   setQuerySettings: { queryShapeHash: "A19F4D5C" },
   settings: {
      "comment": "Legacy reporting query, must not use a specific index."
   }
})
```
The above example assumes the `queryShapeHash` contains a valid value. After applying all the necessary query settings to your destination cluster, your queries will benefit from the same performance optimizations as they did on the source cluster. You can now safely complete the migration cutover process with Percona Link for MongoDB.
