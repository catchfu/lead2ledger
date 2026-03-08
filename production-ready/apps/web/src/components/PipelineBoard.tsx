import type { FC } from "react";
import type { Lead } from "../types";

type PipelineBoardProps = {
  leads: Lead[];
};

const stages: Array<Lead["stage"]> = ["New", "Qualified", "Proposal", "Won"];

const PipelineBoard: FC<PipelineBoardProps> = ({ leads }) => {
  return (
    <section className="panel">
      <h3>Pipeline Board</h3>
      <div className="grid board">
        {stages.map((stage) => {
          const items = leads.filter((lead) => lead.stage === stage);
          return (
            <div className="column" key={stage}>
              <h4>{stage}</h4>
              {items.map((item) => (
                <article className="ticket" key={item.id}>
                  <strong>{item.company}</strong>
                  <span>{item.contact_name}</span>
                  <span>${item.value.toLocaleString()}</span>
                </article>
              ))}
            </div>
          );
        })}
      </div>
    </section>
  );
};

export default PipelineBoard;
