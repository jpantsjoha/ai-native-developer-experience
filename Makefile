PYTHON ?= python3
SKILL_ROOT := .agents/skills/operating-model-bootstrap

.PHONY: lint typecheck planning test spec-conformance check hygiene

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
	# Standard-library compile and shell syntax gate; projects may add a stricter static type checker.
	$(PYTHON) -m py_compile \
		$(SKILL_ROOT)/scripts/bootstrap_operating_model.py \
		$(SKILL_ROOT)/scripts/inspect_repo.py \
		$(SKILL_ROOT)/scripts/validate_operating_model.py \
		scripts/validate_plugin.py \
		scripts/validate_delivery.py \
		scripts/lane_hygiene.py \
		scripts/routing_eval.py \
		tests/test_adoption_journey.py \
		tests/test_delivery_validation.py \
		tests/test_inspect_repo.py \
		tests/test_lane_hygiene.py \
		tests/test_lean_context.py \
		tests/test_operating_model.py \
		tests/test_orchestrator_entry.py \
		tests/test_plugin_packaging.py \
		tests/test_release_contract.py \
		tests/test_review_gate.py
	for s in \
		.githooks/pre-commit \
		hooks/session-start \
		scripts/context-graph-refresh.sh \
		scripts/review-gate.sh \
		skills/cloud-checkup/scripts/cloud_checkup.sh \
		skills/cloud-checkup/scripts/notify.sh \
		skills/system-performance-guardrail/scripts/perf-guardrail.sh; do \
		bash -n "$$s" || exit 1; \
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

# Read-only lane cleanup report (worktrees, branches, stale registrations). Warn-only: it is
# not part of `check` and never deletes. Add HYGIENE_ARGS=--pr-state to consult gh.
hygiene:
	$(PYTHON) scripts/lane_hygiene.py --root . $(HYGIENE_ARGS)

hooks: ## Activate the version-controlled git hooks (markdown lint + independent review gate)
	git config core.hooksPath .githooks
	@echo "git hooks active: .githooks/pre-commit (markdown lint; the review gate is opt-in: REVIEW_GATE=async|block or git config review.gate; on demand: scripts/review-gate.sh --staged | --pr N)"
