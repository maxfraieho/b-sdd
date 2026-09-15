# Plan 002: Utopia DB Integration

## Architecture
- `UtopiaDBAdapter` in `src/adapters/utopia_db.py`.
- SSH tunnel via `sshpass` into `utopia-db` Docker container.
- Stored procedure execution for atomic supersessions.
- Batch transaction execution for knowledge graph sync.
