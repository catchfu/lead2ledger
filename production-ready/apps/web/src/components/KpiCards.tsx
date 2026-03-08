import type { FC } from "react";

type KpiCardsProps = {
  totalPipeline: number;
  wonDeals: number;
  syncSuccessRate: number;
  failedJobs: number;
};

const KpiCards: FC<KpiCardsProps> = ({ totalPipeline, wonDeals, syncSuccessRate, failedJobs }) => {
  const cards = [
    { label: "Total Pipeline", value: `$${totalPipeline.toLocaleString()}` },
    { label: "Won Deals", value: wonDeals.toString() },
    { label: "Sync Success", value: `${syncSuccessRate}%` },
    { label: "Failed Jobs", value: failedJobs.toString() }
  ];

  return (
    <section className="grid cards">
      {cards.map((card) => (
        <article className="card" key={card.label}>
          <p className="muted">{card.label}</p>
          <h2>{card.value}</h2>
        </article>
      ))}
    </section>
  );
};

export default KpiCards;
