import { useCallback, useEffect, useState } from "react";
import Header from "./components/Header";
import KpiCards from "./components/KpiCards";
import LeadsTable from "./components/LeadsTable";
import PipelineBoard from "./components/PipelineBoard";
import SyncStatus from "./components/SyncStatus";
import {
  clearToken,
  createLead,
  fetchLeads,
  fetchMe,
  fetchSummary,
  fetchSyncJobs,
  getToken,
  login
} from "./api";
import type { AuthUser, DashboardSummary, Lead, LeadStage, SyncJob } from "./types";

const emptySummary: DashboardSummary = {
  total_pipeline: 0,
  won_deals: 0,
  sync_success_rate: 0,
  failed_jobs: 0
};

function App() {
  const [apiStatus, setApiStatus] = useState<"online" | "offline">("offline");
  const [summary, setSummary] = useState<DashboardSummary>(emptySummary);
  const [leads, setLeads] = useState<Lead[]>([]);
  const [syncJobs, setSyncJobs] = useState<SyncJob[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>("");

  const [company, setCompany] = useState("");
  const [contact, setContact] = useState("");
  const [stage, setStage] = useState<LeadStage>("New");
  const [value, setValue] = useState("1000");

  const [username, setUsername] = useState("alice");
  const [password, setPassword] = useState("alice123");
  const [user, setUser] = useState<AuthUser | null>(null);

  const loadData = useCallback(async () => {
    try {
      setLoading(true);
      setError("");
      const [summaryData, leadData, jobData] = await Promise.all([
        fetchSummary(),
        fetchLeads(),
        fetchSyncJobs()
      ]);
      setSummary(summaryData);
      setLeads(leadData);
      setSyncJobs(jobData);
      setApiStatus("online");
    } catch (e) {
      setApiStatus("offline");
      setError(e instanceof Error ? e.message : "Failed to load API data");
    } finally {
      setLoading(false);
    }
  }, []);

  const bootstrap = useCallback(async () => {
    if (!getToken()) {
      setLoading(false);
      return;
    }
    try {
      const me = await fetchMe();
      setUser(me);
      await loadData();
    } catch {
      clearToken();
      setUser(null);
      setLoading(false);
    }
  }, [loadData]);

  useEffect(() => {
    void bootstrap();
  }, [bootstrap]);

  const onLogin = async (event: React.FormEvent) => {
    event.preventDefault();
    try {
      setError("");
      await login(username, password);
      const me = await fetchMe();
      setUser(me);
      await loadData();
    } catch (e) {
      clearToken();
      setUser(null);
      setError(e instanceof Error ? e.message : "Login failed");
    }
  };

  const onLogout = () => {
    clearToken();
    setUser(null);
    setLeads([]);
    setSyncJobs([]);
    setSummary(emptySummary);
  };

  const onAddLead = async (event: React.FormEvent) => {
    event.preventDefault();
    try {
      await createLead({
        company,
        contact_name: contact,
        stage,
        value: Number(value)
      });
      setCompany("");
      setContact("");
      setStage("New");
      setValue("1000");
      await loadData();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to create lead");
    }
  };

  if (!user) {
    return (
      <main className="container">
        <section className="panel auth-panel">
          <h2>Login</h2>
          <p>Use seeded users: `alice/alice123`, `sam/sam123`, `fiona/fiona123`, `omar/omar123`, `gina/gina123`.</p>
          {error && <div className="error">{error}</div>}
          <form className="auth-form" onSubmit={onLogin}>
            <input value={username} onChange={(e) => setUsername(e.target.value)} placeholder="Username" required />
            <input
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Password"
              type="password"
              required
            />
            <button type="submit">Sign in</button>
          </form>
        </section>
      </main>
    );
  }

  return (
    <main className="container">
      <Header apiStatus={apiStatus} user={user} onLogout={onLogout} />
      {error && <div className="error">{error}</div>}
      <KpiCards
        totalPipeline={summary.total_pipeline}
        wonDeals={summary.won_deals}
        syncSuccessRate={summary.sync_success_rate}
        failedJobs={summary.failed_jobs}
      />
      {(user.role === "admin" || user.role === "sales") && (
        <section className="panel">
          <h3>Add Lead</h3>
          <form className="lead-form" onSubmit={onAddLead}>
            <input value={company} onChange={(e) => setCompany(e.target.value)} placeholder="Company" required />
            <input value={contact} onChange={(e) => setContact(e.target.value)} placeholder="Contact name" required />
            <select value={stage} onChange={(e) => setStage(e.target.value as LeadStage)}>
              <option>New</option>
              <option>Qualified</option>
              <option>Proposal</option>
              <option>Won</option>
            </select>
            <input value={value} onChange={(e) => setValue(e.target.value)} type="number" min="1" step="0.01" required />
            <button type="submit">Create</button>
            <button type="button" onClick={() => void loadData()}>Refresh</button>
          </form>
        </section>
      )}
      {loading ? (
        <section className="panel">Loading dashboard data...</section>
      ) : (
        <>
          <section className="grid two-col">
            <PipelineBoard leads={leads} />
            <SyncStatus jobs={syncJobs} />
          </section>
          <LeadsTable leads={leads} />
        </>
      )}
    </main>
  );
}

export default App;
