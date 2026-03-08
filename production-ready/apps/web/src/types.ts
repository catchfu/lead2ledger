export type LeadStage = "New" | "Qualified" | "Proposal" | "Won";
export type SyncState = "Synced" | "Pending" | "Failed";
export type JobState = "Success" | "Retrying" | "Failed";
export type Role = "admin" | "sales" | "ops" | "finance";

export type Lead = {
  id: string;
  company: string;
  contact_name: string;
  stage: LeadStage;
  value: number;
  sap_sync: SyncState;
  created_at: string;
};

export type SyncJob = {
  id: string;
  entity: "Customer" | "Quote" | "Order" | "Invoice";
  direction: "CRM->SAP" | "SAP->CRM";
  status: JobState;
  payload_ref: string;
  updated_at: string;
};

export type DashboardSummary = {
  total_pipeline: number;
  won_deals: number;
  sync_success_rate: number;
  failed_jobs: number;
};

export type AuthUser = {
  username: string;
  full_name: string;
  role: Role;
  tenant_id: string;
};

export type LoginResponse = {
  access_token: string;
  token_type: "bearer";
  expires_at: string;
};
