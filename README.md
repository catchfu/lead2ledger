# Lead2Ledger

Lead2Ledger is a CRM + SAP integration platform for small businesses, with role-based access, tenant isolation, and lead-to-cash workflow support.

## Repository Structure
- `production-ready/apps/api`: FastAPI backend (auth, RBAC, tenant-scoped CRM + sync APIs)
- `production-ready/apps/web`: React + TypeScript frontend dashboard
- `production-ready/docs`: PRD, architecture, integration, testing, deployment, BA docs
- `production-ready/infra`: local infrastructure templates
- `production-ready/tests`: API contract test specs

## Quick Start
### API
```bash
cd production-ready/apps/api
python main.py
```

### Web
```bash
cd production-ready/apps/web
cp .env.example .env
npm install
npm run dev
```

Set `VITE_API_URL` in `production-ready/apps/web/.env` if needed.

## Default Auth (Seed Users)
- `alice / alice123` (admin, tenant: acme)
- `sam / sam123` (sales, tenant: acme)
- `fiona / fiona123` (finance, tenant: acme)
- `omar / omar123` (ops, tenant: acme)
- `gina / gina123` (admin, tenant: globex)
