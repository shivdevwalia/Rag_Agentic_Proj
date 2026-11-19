# Docker Operations

## Starting the database
Start Docker Desktop with its Linux container engine, then run docker compose up -d --wait from the project root. The wait option lets Compose report when the configured health check succeeds.

## Checking status
Use docker compose ps to inspect service status. The health check uses pg_isready to test whether PostgreSQL is accepting connections. This is useful operational evidence, but it does not prove that a particular application table exists.

## Persistent data
The postgres_data named volume stores database files independently of the container. Running docker compose down stops and removes the project's containers while retaining that named volume.

## Initialization behavior
Scripts mounted under /docker-entrypoint-initdb.d run during initial database creation. They do not rerun every time a container starts with an existing data volume. Editing the initialization SQL therefore does not automatically migrate an existing database.

## Troubleshooting
If connections fail, inspect Docker Desktop, container health, the configured port, and database credentials. If the port is occupied, choose another POSTGRES_PORT and recreate the service. Avoid deleting the data volume as a routine troubleshooting step.

