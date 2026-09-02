# Architecture and governance workflow

The deterministic generator creates independently recorded orders, escrow events, and finance transactions. PostgreSQL holds raw records; dbt types, tests, joins, and publishes governed marts. The registry owns KPI definition, grain, owner, and version. The drift service compares independently exported BI results with governed values.

A pull request changing metric meaning must include impact analysis and owner approval. Additive definitions receive a minor release; corrections retain an audit note; grain or meaning changes create a new major definition. A dashboard remains uncertified while its reported result exceeds tolerance.

The dependency-light evaluator keeps CI fast. PostgreSQL and dbt form the production-shaped execution route. A real BI adapter can replace the deterministic JSON export without changing governance behavior.
