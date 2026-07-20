PYTHON ?= python3
SKILL_ROOT := .agents/skills/operating-model-bootstrap

.PHONY: lint typecheck test check

lint:
	@if command -v markdownlint-cli2 >/dev/null 2>&1; then \
		markdownlint-cli2 '**/*.md'; \
	elif command -v npx >/dev/null 2>&1; then \
		npx --yes markdownlint-cli2 '**/*.md'; \
	else \
		echo 'ERROR: install markdownlint-cli2 or Node.js/npm' >&2; \
		exit 1; \
	fi

typecheck:
	# Standard-library compile gate; projects may add a stricter static type checker.
	$(PYTHON) -m py_compile \
		$(SKILL_ROOT)/scripts/bootstrap_operating_model.py \
		$(SKILL_ROOT)/scripts/validate_operating_model.py \
		scripts/validate_plugin.py \
		tests/test_operating_model.py \
		tests/test_plugin_packaging.py

test:
	$(PYTHON) -m unittest discover -s tests -p 'test_*.py'
	$(PYTHON) $(SKILL_ROOT)/scripts/validate_operating_model.py \
		--template-root $(SKILL_ROOT)
	$(PYTHON) scripts/validate_plugin.py --root .

check: lint typecheck test
