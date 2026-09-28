export default function FailedScreen({ reason, onRetry, onStartOver }) {
  return (
    <div className="status-screen">
      <div className="status-icon is-failed">✕</div>
      <h2 className="status-title">Payment didn't go through</h2>
      <p className="status-detail">{reason || "The payment was cancelled or timed out."}</p>

      <button className="primary-button" onClick={onRetry}>
        Try again
      </button>
      <button className="secondary-button" onClick={onStartOver}>
        Choose a different plan
      </button>
    </div>
  );
}
