# Harness targets written by operating-model-bootstrap --make-targets (devex-charter).
# Included from the Makefile with `-include .devex/harness.mk`; safe to edit, never overwritten.
PYTHON ?= python3
RATCHET_BASE ?= origin/main

.PHONY: harness-install harness-status ratchet ratchet-raise registration-audit

harness-install: ## install the harness pre-commit into this clone (never writes outside it)
	$(PYTHON) .devex/hooks/install-precommit.py

harness-status: ## report whether the harness pre-commit is installed in this clone
	@hooks="$$(git rev-parse --git-common-dir)/hooks/pre-commit"; \
	if [ -f "$$hooks" ] && grep -q "devex-charter harness pre-commit" "$$hooks"; then \
		echo "harness pre-commit: INSTALLED ($$hooks)"; \
	else echo "harness pre-commit: NOT INSTALLED (make harness-install)"; exit 1; fi

ratchet: ## literal ratchet over the whole tree
	$(PYTHON) .devex/hooks/literal-ratchet.py

ratchet-raise: ## baseline may not rise against $(RATCHET_BASE) without a reasoned note
	$(PYTHON) .devex/hooks/literal-ratchet.py --check-raise $(RATCHET_BASE)

registration-audit: ## every test script is registered with a runner or excluded with a reason
	$(PYTHON) .devex/tools/registration-audit.py
