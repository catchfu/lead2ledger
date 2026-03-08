# Lead2Ledger

Lead2Ledger is a CRM + SAP integration platform for small businesses, with role-based access, tenant isolation, and lead-to-cash workflow support.

## Repository Structure
- `apps/api`: FastAPI backend (auth, RBAC, tenant-scoped CRM + sync APIs)
- `apps/web`: React + TypeScript frontend dashboard
- `docs`: PRD, architecture, integration, testing, deployment, and BA docs
- `infra`: local infrastructure templates
- `tests`: API contract test specs

## Quick Start
### API
```bash
cd apps/api
python main.py
```

### Web
```bash
cd apps/web
cp .env.example .env
npm install
npm run dev
```

Set `VITE_API_URL` in `apps/web/.env` if needed.

## Default Auth (Seed Users)
- `alice / alice123` (admin, tenant: acme)
- `sam / sam123` (sales, tenant: acme)
- `fiona / fiona123` (finance, tenant: acme)
- `omar / omar123` (ops, tenant: acme)
- `gina / gina123` (admin, tenant: globex)
