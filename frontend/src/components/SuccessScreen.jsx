import { useState } from "react";

export default function SuccessScreen({ order, onStartOver }) {
  const [copied, setCopied] = useState(false);

  async function handleCopy() {
    try {
      await navigator.clipboard.writeText(order.voucher_code);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // Clipboard API can be unavailable (older browsers, non-HTTPS) — the
      // code is still selectable on screen, so this is a soft failure.
    }
  }

  return (
    <div className="status-screen">
      <div className="status-icon is-success">✓</div>
      <h2 className="status-title">You're connected</h2>
      <p className="status-detail">Payment confirmed. Here's your access code.</p>

      <div className="voucher-box">
        <p className="voucher-label">Voucher code</p>
        <p className="voucher-code" onClick={handleCopy} title="Tap to copy">
          {order.voucher_code}
        </p>
        {copied && <p className="voucher-copied">Copied</p>}
        {order.expires_at && (
          <p className="voucher-expiry">
            Valid until {new Date(order.expires_at).toLocaleString()}
          </p>
        )}
      </div>

      <button className="secondary-button" onClick={onStartOver}>
        Buy another plan
      </button>
    </div>
  );
}
 