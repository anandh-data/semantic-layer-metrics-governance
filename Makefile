.PHONY: test demo
test:
	PYTHONPATH=src python3 -m unittest discover -s tests -v
demo:
	PYTHONPATH=src python3 -m metric_hub.cli; test $$? -eq 1
