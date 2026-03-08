# SAP Integration Specification

## Integration Patterns
- Near-real-time event-driven sync for transactional updates.
- Scheduled reconciliation for drift correction.
- Idempotent upserts keyed by external reference IDs.

## Key Flows
1. Customer upsert (CRM -> SAP)
2. Product catalog sync (SAP -> CRM)
3. Quote/order handoff (CRM -> SAP)
4. Invoice and payment status sync (SAP -> CRM)

## Reliability
- Exponential backoff retries
- Dead-letter queue with operator replay
- Correlation IDs for traceability

## Conflict Rules
- Master system by domain:
  - SAP: products/pricing/tax/inventory
  - CRM: lead/opportunity/activity
- Last-write-wins only for non-authoritative mirrored fields
