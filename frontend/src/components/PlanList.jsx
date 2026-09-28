import SignalMeter from "./SignalMeter.jsx";

export default function PlanList({ plans, loading, error, onSelect, onRetry }) {
  if (loading) {
    return <p className="empty-state">Loading plans…</p>;
  }

  if (error) {
    return (
      <div className="error-state">
        <p>{error}</p>
        <button className="secondary-button" onClick={onRetry}>
          Try again
        </button>
      </div>
    );
  }

  if (plans.length === 0) {
    return <p className="empty-state">No plans available right now — check back shortly.</p>;
  }

  const maxSpeed = Math.max(...plans.map((p) => p.speed_mbps));

  return (
    <div className="plan-list">
      {plans.map((plan) => (
        <button key={plan.id} className="plan-row" onClick={() => onSelect(plan)}>
          <SignalMeter speedMbps={plan.speed_mbps} maxSpeed={maxSpeed} />
          <div className="plan-row__info">
            <p className="plan-row__name">{plan.name}</p>
            <p className="plan-row__meta">
              {plan.speed_mbps} Mbps · {formatDuration(plan.duration_hours)}
            </p>
          </div>
          <div className="plan-row__price">
            KES {plan.price_kes}
          </div>
        </button>
      ))}
    </div>
  );
}

function formatDuration(hours) {
  if (hours < 24) return `${hours}h access`;
  const days = Math.round(hours / 24);
  return `${days} day${days > 1 ? "s" : ""} access`;
}
