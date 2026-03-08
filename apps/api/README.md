# CRM + SAP API

## Run
```bash
python main.py
```

## Environment
- `CRM_DB_PATH` (default: `apps/api/crm.db`)
- `JWT_SECRET` (required for secure deployments)
- `ACCESS_TOKEN_TTL_MINUTES` (default: `120`)

## Auth Flow
1. `POST /auth/login` with username/password.
2. Use `Authorization: Bearer <token>` for all protected endpoints.
3. Inspect session identity with `GET /auth/me`.

## Seeded Users
- `alice / alice123` -> `admin` (tenant `acme`)
- `sam / sam123` -> `sales` (tenant `acme`)
- `fiona / fiona123` -> `finance` (tenant `acme`)
- `omar / omar123` -> `ops` (tenant `acme`)
- `gina / gina123` -> `admin` (tenant `globex`)

## RBAC
- Leads create: `admin`, `sales`
- Sync jobs create: `admin`, `ops`, `sales`
- Sync job status update: `admin`, `ops`
- Dashboard/leads/list endpoints: any authenticated role

All data endpoints are tenant-scoped from JWT claims.
