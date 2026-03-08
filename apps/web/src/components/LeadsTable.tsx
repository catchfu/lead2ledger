import type { FC } from "react";
import type { Lead } from "../types";

type LeadsTableProps = {
  leads: Lead[];
};

const LeadsTable: FC<LeadsTableProps> = ({ leads }) => {
  return (
    <section className="panel">
      <h3>Leads</h3>
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Company</th>
            <th>Contact</th>
            <th>Stage</th>
            <th>Amount</th>
            <th>SAP Sync</th>
          </tr>
        </thead>
        <tbody>
          {leads.map((lead) => (
            <tr key={lead.id}>
              <td>{lead.id}</td>
              <td>{lead.company}</td>
              <td>{lead.contact_name}</td>
              <td>{lead.stage}</td>
              <td>${lead.value.toLocaleString()}</td>
              <td>{lead.sap_sync}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  );
};

export default LeadsTable;
