# Deployment guide

## Verified local execution

The repository can run against an isolated Homebrew PostgreSQL cluster:

```bash
make local-db-start
make pipeline
make integration-test
make local-db-stop
```

## Container execution

Copy `.env.example` to `.env`, change the password, then run:

```bash
docker compose up -d --wait postgres
docker compose run --rm pipeline
```

The output directories are bind-mounted, so the container writes the same data, logs, reports, dashboard, and screenshots as the verified local path.

## Production adaptation

Use managed PostgreSQL or a cloud warehouse, a secrets manager, workload identity, TLS, private networking, object storage for immutable Parquet, and an orchestrator service. Run migrations separately from application startup. Publish generated reports to artifact storage and send certification status to the BI release process.

Never use the committed local password outside an isolated developer machine.
