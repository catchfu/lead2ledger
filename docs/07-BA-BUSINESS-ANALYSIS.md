# Business Analysis Document

## Scope
CRM + SAP solution for SMB sales, operations, and finance workflows.

## Core Business Processes
1. Lead capture to qualification in CRM.
2. Opportunity management with pipeline stages and weighted forecasting.
3. Quote and sales order handoff from CRM to SAP.
4. Invoice and payment feedback from SAP to CRM.
5. Customer support and account health follow-up from CRM timeline.

## Functional Requirements
- FR-1: Manage leads, contacts, accounts, opportunities, and activities.
- FR-2: Enforce stage transition rules with required data checks.
- FR-3: Sync customer master data between CRM and SAP using external reference IDs.
- FR-4: Sync product catalog and pricing from SAP to CRM on schedule and on demand.
- FR-5: Create quote/order in CRM and post to SAP with status tracking.
- FR-6: Ingest invoice and payment status from SAP back to CRM timeline.
- FR-7: Provide role-based visibility for sales rep, manager, operations, finance, and admin.
- FR-8: Preserve audit history for critical updates and sync operations.

## Non-Functional Requirements
- NFR-1: P95 API latency under 300ms for core CRM reads.
- NFR-2: Integration retries with dead-letter handling for failed sync events.
- NFR-3: RPO <= 15 minutes and RTO <= 60 minutes for production incidents.
- NFR-4: Tenant-level logical isolation and encrypted sensitive fields.
- NFR-5: Monitoring coverage for job failures, queue depth, and sync latency.

## Data Ownership Rules
- SAP is system of record for product, pricing, tax, inventory, invoice, and payment status.
- CRM is system of record for lead, opportunity, activity, and sales notes.
- Shared entities use external IDs and idempotent upsert semantics.

## BA Acceptance Criteria
- Business flow lead->quote->order->invoice validated end-to-end.
- Data mapping sign-off completed for customer, product, quote/order, and invoice entities.
- Exception handling workflow approved for failed sync and duplicate records.
- Role and permissions matrix approved by sales and finance owners.
