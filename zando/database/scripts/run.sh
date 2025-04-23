poetry run python db_migrations/cli.py --direction down && \
  poetry run python db_migrations/cli.py --direction up && \
  poetry run python db_migrations/cli.py --direction populate --data-dir ./data/production
