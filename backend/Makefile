PHASE5_MIGRATION=backend/migrations/20251001_add_phase5_ml_columns.sql
BACKFILL_SCRIPT=backend/scripts/phase5_backfill.py

.PHONY: phase5-migrate phase5-backfill phase5-backfill-dry

## Apply Phase 5 database migration (requires DATABASE_URL pointing to Postgres/Supabase)
phase5-migrate:
	@if [ -z "$$DATABASE_URL" ]; then \
		echo "DATABASE_URL not set. Export your Postgres connection string before running."; \
		exit 1; \
	fi
	psql "$$DATABASE_URL" -f $(PHASE5_MIGRATION)

## Backfill ML feature vectors into pattern_events (set LIMIT for batch size, defaults to all)
phase5-backfill:
	python $(BACKFILL_SCRIPT) --limit $${LIMIT:-0}

## Backfill preview without writing changes (set LIMIT to restrict row count)
phase5-backfill-dry:
	python $(BACKFILL_SCRIPT) --limit $${LIMIT:-200} --dry-run
