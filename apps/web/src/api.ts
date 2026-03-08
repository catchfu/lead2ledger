import type { AuthUser, DashboardSummary, Lead, LoginResponse, SyncJob } from "./types";

const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";
const TOKEN_KEY = "crm_auth_token";

let authToken = localStorage.getItem(TOKEN_KEY) ?? "";

function authHeaders(): Record<string, string> {
  if (!authToken) {
    return {};
  }
  return { Authorization: `Bearer ${authToken}` };
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...authHeaders(),
      ...(init?.headers ?? {})
    },
    ...init
  });

  if (!res.ok) {
    const details = await res.text();
    throw new Error(`API ${res.status}: ${details || res.statusText}`);
  }

  return (await res.json()) as T;
}

export function getToken(): string {
  return authToken;
}

export function setToken(token: string): void {
  authToken = token;
  localStorage.setItem(TOKEN_KEY, token);
}

export function clearToken(): void {
  authToken = "";
  localStorage.removeItem(TOKEN_KEY);
}

export async function login(username: string, password: string): Promise<LoginResponse> {
  const res = await request<LoginResponse>("/auth/login", {
    method: "POST",
    body: JSON.stringify({ username, password })
  });
  setToken(res.access_token);
  return res;
}

export async function fetchMe(): Promise<AuthUser> {
  return request<AuthUser>("/auth/me");
}

export async function fetchSummary(): Promise<DashboardSummary> {
  return request<DashboardSummary>("/dashboard/summary");
}

export async function fetchLeads(): Promise<Lead[]> {
  return request<Lead[]>("/crm/leads");
}

export async function fetchSyncJobs(): Promise<SyncJob[]> {
  return request<SyncJob[]>("/sap/sync/jobs");
}

export async function createLead(payload: {
  company: string;
  contact_name: string;
  stage: "New" | "Qualified" | "Proposal" | "Won";
  value: number;
}): Promise<Lead> {
  return request<Lead>("/crm/leads", {
    method: "POST",
    body: JSON.stringify(payload)
  });
}
