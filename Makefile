PYTHON ?= python3
SKILL_ROOT := .agents/skills/operating-model-bootstrap

.PHONY: lint typecheck planning test spec-conformance check

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
	# Syntax gate, not semantic type checking; never execute hooks or providers here.
	$(PYTHON) -m compileall -q -f scripts tests $(SKILL_ROOT)/scripts
	@for file in scripts/*.sh hooks/session-start .githooks/pre-commit; do \
		bash -n "$$file" || exit 1; \
	done

planning:
	$(PYTHON) scripts/validate_delivery.py --root .

test:
	$(PYTHON) -m unittest discover -s tests -p 'test_*.py'
	$(PYTHON) $(SKILL_ROOT)/scripts/validate_operating_model.py \
		--template-root $(SKILL_ROOT)
	$(PYTHON) scripts/validate_plugin.py --root .
	$(MAKE) planning

# Agent Plugins 1.0.0 + Agent Skills conformance, isolated from the drift checks so the
# standard reports as its own signal. https://agent-plugins.org/specification
spec-conformance:
	$(PYTHON) scripts/validate_plugin.py --root . --spec-only

check: lint typecheck test spec-conformance

hooks: ## Activate the version-controlled git hooks (markdown lint + independent review gate)
	git config core.hooksPath .githooks
	@echo "git hooks active: .githooks/pre-commit (markdown lint; the review gate is opt-in: REVIEW_GATE=async|block or git config review.gate; on demand: scripts/review-gate.sh --staged | --pr N)"
