
- Project description:

- Technologies utilized:
    - Docker
    - Airflow
    - PostgreSQL
    - Linux/Debian
    - AWS
        - S3 
        - Redshift
    - Tableau

- Pipeline DAGs 
    - rest_to_postgres
    - archive_postgres_to_s3
        - This DAG will handle moving processed data from postgres to AWS s3. S3 will be used for cold storage, data not readily accessed, but will always be available for auditing, compliance, and historical data for future use. This long term storage should be cost efficient, employing the parquet file format, and should also be well organized, using partitioning strategies like simple key-values within an s3 bucket.
        - S3 will also have a bucket dedicated to storing logs for bug testing and historical purposes. This is mainly handled by Docker and Airflow logging handled by a Fluentbit, logging processor. 
    - postgres_to_redshift
    - postgres_cleanup