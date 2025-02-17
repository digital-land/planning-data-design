#!/bin/bash
set -e

echo "Restoring database from backup..."
# Add a small delay to ensure database is ready
sleep 2

# Restore the backup
pg_restore -U postgres -d planning-data-design --no-owner --no-privileges -v /docker-entrypoint-initdb.d/latest_backup.dump || true
