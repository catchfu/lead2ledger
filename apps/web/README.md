# CRM + SAP Web App

## What is included
- React + TypeScript + Vite setup
- Live API integration (no mock data)
- CRM dashboard:
  - KPI cards from `/dashboard/summary`
  - Pipeline board from `/crm/leads`
  - Leads table from `/crm/leads`
  - SAP sync status from `/sap/sync/jobs`
- Lead creation form posting to `/crm/leads`

## Run locally
```bash
cp .env.example .env
npm install
npm run dev
```

## API base URL
Set `VITE_API_URL` in `.env` (default: `http://localhost:8000`).

## Build
```bash
npm run build
npm run preview
```
