# Solution Architecture

## Stack
- Frontend: React + TypeScript
- API: FastAPI + Python
- DB: PostgreSQL
- Queue: Redis + worker
- Integration: SAP connector service (REST/OData/B1 Service Layer)

## Services
- `crm-api`: CRM domain API
- `sap-connector`: Mapping, retries, idempotency, SAP transport
- `sync-worker`: Async jobs, dead-letter handling
- `web-app`: Sales and operations UI

## Data Domains
- CRM: leads, accounts, contacts, opportunities, activities
- Commercial: quotes, sales_orders, invoices
- Master data: products, price lists, tax codes
- Integration: sync_jobs, sync_events, external_refs

## Security
- JWT auth + RBAC
- Tenant isolation
- PII encryption at rest
- Full audit trails
