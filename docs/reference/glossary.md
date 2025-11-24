# Glossary

## ACID
     
Set of properties that guarantee database transactions are processed reliably. Stands for [`Atomicity`](#atomicity), [`Consistency`](#consistency), [`Isolation`](#isolation), [`Durability`](#durability).

## Atomicity

Atomicity means that database operations are applied following an "all or nothing" rule. A transaction is either fully applied or not at all.

## Blob
    
A blob stands for Binary Large Object, which includes objects such as images and multimedia files. In other words these are various data files that you store in Microsoft's data storage platform. Blobs are organized in [containers](#container) which are kept in Azure Blob storage under your storage account.

## Bucket

A bucket is a container on the s3 remote storage that stores backups.

## Change replication 

An ongoing process of replicating modifications to collections, views, indexes, and documents after initial copying.

## Clone changes catchup

The process of applying changes that occurred during the cloning period to ensure consistency between source and target.

## Cluster replication 

The process of copying user data, collections, views, and indexes from a primary (source) cluster to a secondary (target) cluster. Initiated by POST /start command, it transitions PLM status to running, and completes when the PLM status becomes finalized.

## Collection
     
A collection is the way data is organized in MongoDB. It is analogous to a table in relational databases.

## Consistency

In the context of backup and restore, consistency means that the data restored will be consistent in a given point in time. Partial or incomplete writes to disk of atomic operations (for example, to table and index data structures separately) won't be served to the client after the restore. The same applies to multi-document transactions that started but didn't complete by the time the backup was finished.

## Container

A container in Microsoft Azure Blob storage organizes a set of [blobs](#blob), similar to a directory in a file system. It can include an unlimited number of blobs.

A container name must be a valid DNS name, as it forms part of the unique URI (Uniform resource identifier) used to address the container or its blobs. 

## Data clone

A base operation of copying collections, views, selected indexes, and documents. Produces inconsistent data without accompanying change replication.

## Durability
   
Once a transaction is committed, it will remain so.

## Finalization 

A critical process that converts temporary changes into their original form from the source cluster, ensuring complete consistency.

## Initial sync

Initial sync is the process of copying all data from a source to a target system. In MongoDB, this occurs when a new node joins a replica set, where it copies all databases, collections, and indexes from an existing member. In the context of Percona Link for MongoDB (PLM), initial sync is the first phase of data migration where all existing data is copied from the source cluster to the target cluster. Then PLM applies the changes that occurred to data since the initial sync start.

## Isolation

The Isolation requirement means that no transaction can interfere with another.

## Percona Server for MongoDB 

Percona Server for MongoDB is a drop-in replacement for MongoDB Community Edition with enterprise-grade features.

## Persistent Query Settings

Persistent Query Settings (PQS) in MongoDB are a way to define and retain query behavior (like index hints, rejection filters, or other optimizer inputs) for a given query shape across the entire cluster. Unlike temporary index filters, PQS are cluster-wide and survive restarts.

## Replica set
   
A replica set is a group of `mongod` nodes that host the same data set.

## Replication

Replication is the process of synchronizing data across multiple database instances and database deployments to ensure availability, redundancy, and consistency. It allows changes in one database (or cluster) to be reflected in another.

## Replication status 

Indicators like idle, running, paused, failed, finalizing, and finalized that reflect the current state of replication.

## Replication lag 

Logical time difference between when a change occurs on the source cluster and when it's applied to the target cluster.

## Source

A source deployment is where the data is copied during an initial sync and then replicated to a target.

## Target 

A target deployment is where the data is replicated to.

## Technical preview feature

Technical preview features are not yet ready for enterprise use and are not included in support via SLA. They are included in this release so that users can provide feedback prior to the full release of the feature in a future GA release (or removal of the feature if it is deemed not useful). This functionality can change (APIs, CLIs, etc.) from tech preview to GA. 

