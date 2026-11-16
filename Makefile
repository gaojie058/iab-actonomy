PYTHON ?= python3

.PHONY: help check test demo codebook crosswalk
help:
	@$(PYTHON) scripts/actonomy.py --help

check:
	$(PYTHON) scripts/actonomy.py check
	$(PYTHON) scripts/check_docs.py
	$(PYTHON) -m unittest discover -s tests -v

test:
	$(PYTHON) -m unittest discover -s tests -v

demo:
	$(PYTHON) scripts/actonomy.py demo

codebook:
	$(PYTHON) scripts/actonomy.py codebook

crosswalk:
	$(PYTHON) scripts/actonomy.py crosswalk
