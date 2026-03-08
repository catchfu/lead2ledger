# Deployment Runbook

## Environments
- dev, staging, production

## Release Steps
1. Run migrations
2. Deploy API + worker
3. Deploy SAP connector
4. Deploy frontend
5. Run smoke tests
6. Enable monitoring alerts

## Rollback
- Revert service image tag
- Roll back migration only when backward-compatible checks pass
- Replay pending sync events after recovery
