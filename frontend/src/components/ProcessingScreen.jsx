import SignalMeter from "./SignalMeter.jsx";

export default function ProcessingScreen({ phone, timedOut, onCheckAgain, onCancel }) {
  return (
    <div className="status-screen">
      <SignalMeter pulsing />
      {timedOut ? (
        <>
          <h2 className="status-title">Still waiting on that payment</h2>
          <p className="status-detail">
            It's taking longer than usual. If you already paid, check again — otherwise the
            prompt may have expired.
          </p>
          <button className="primary-button" onClick={onCheckAgain}>
            Check again
          </button>
        </>
      ) : (
        <>
          <h2 className="status-title">Check your phone</h2>
          <p className="status-detail">
            We sent an M-Pesa prompt to {phone}. Enter your PIN to complete payment.
          </p>
        </>
      )}
      <button className="secondary-button" onClick={onCancel}>
        Cancel and start over
      </button>
    </div>
  );
}
