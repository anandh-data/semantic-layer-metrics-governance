import os
import unittest

from metric_hub.config import Settings
from metric_hub.database import fetch_rows


@unittest.skipUnless(os.getenv("RUN_DB_TESTS") == "1", "set RUN_DB_TESTS=1 with local PostgreSQL running")
class PostgresIntegrationTests(unittest.TestCase):
    def test_raw_and_mart_counts_match(self):
        settings = Settings()
        _, rows = fetch_rows(settings.dsn, "select (select count(*) from raw.orders), (select count(*) from analytics.fct_order_performance)")
        self.assertEqual(rows[0][0], rows[0][1])
        self.assertGreater(rows[0][0], 0)

    def test_no_orphaned_finance_transactions(self):
        settings = Settings()
        _, rows = fetch_rows(settings.dsn, "select count(*) from raw.finance_transactions f left join raw.orders o using(order_id) where o.order_id is null")
        self.assertEqual(rows[0][0], 0)
