import type { FC } from "react";
import type { AuthUser } from "../types";

type HeaderProps = {
  apiStatus: "online" | "offline";
  user: AuthUser;
  onLogout: () => void;
};

const Header: FC<HeaderProps> = ({ apiStatus, user, onLogout }) => {
  return (
    <header className="header">
      <div>
        <h1>CRM + SAP Control Center</h1>
        <p>Lead-to-cash tracking for small business operations.</p>
        <p className="meta">Tenant: {user.tenant_id} | Role: {user.role}</p>
      </div>
      <div className="header-actions">
        <div className={`pill ${apiStatus}`}>API: {apiStatus}</div>
        <div className="user-info">{user.full_name} ({user.username})</div>
        <button onClick={onLogout}>Logout</button>
      </div>
    </header>
  );
};

export default Header;
