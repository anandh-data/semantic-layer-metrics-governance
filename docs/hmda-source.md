# HMDA source and selection

The mortgage source is the CFPB's public 2017 nationwide HMDA all-records coded file. It contains 14,285,496 privacy-modified loan/application records. The project takes a deterministic systematic sample of 2,800,000 positions across the full published ordering; this avoids the outcome bias that would result from taking an early contiguous block.

The 182 MB source archive and generated Parquet file are intentionally excluded from Git. `make hmda` reproduces the analytical file after the official archive has been downloaded. The committed manifest records the source URL, selection method, columns, record counts, and SHA-256 checksums.

Official references:

- https://www.consumerfinance.gov/data-research/hmda/historic-data/
- https://files.consumerfinance.gov/hmda-historic-data-dictionaries/lar_record_format.pdf
- https://files.consumerfinance.gov/hmda-historic-data-dictionaries/lar_record_codes.pdf

HMDA does not contain every underwriting factor. The governed metrics describe this published dataset and must not be interpreted as causal evidence of discrimination.
