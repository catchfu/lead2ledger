import type { FC } from "react";
import type { SyncJob } from "../types";

type SyncStatusProps = {
  jobs: SyncJob[];
};

const SyncStatus: FC<SyncStatusProps> = ({ jobs }) => {
  return (
    <section className="panel">
      <h3>SAP Sync Status</h3>
      <ul className="sync-list">
        {jobs.map((job) => (
          <li key={job.id}>
            <div>
              <strong>{job.entity}</strong>
              <span>{job.direction}</span>
            </div>
            <div>
              <span className={`status ${job.status.toLowerCase()}`}>{job.status}</span>
              <span>{new Date(job.updated_at).toLocaleString()}</span>
            </div>
          </li>
        ))}
      </ul>
    </section>
  );
};

export default SyncStatus;
