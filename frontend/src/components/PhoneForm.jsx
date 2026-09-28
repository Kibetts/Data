import { useState } from "react";

// Loose client-side check just to catch obvious typos before hitting the
// network — the backend does the real, authoritative normalization/validation.
function looksLikeKenyanNumber(value) {
  const digits = value.replace(/\D/g, "");
  return (
    (digits.startsWith("07") || digits.startsWith("01")) && digits.length === 10
  ) || (digits.startsWith("254") && digits.length === 12);
}

export default function PhoneForm({ plan, submitting, submitError, onSubmit, onBack }) {
  const [phone, setPhone] = useState("");
  const [touched, setTouched] = useState(false);

  const valid = looksLikeKenyanNumber(phone);

  function handleSubmit(e) {
    e.preventDefault();
    setTouched(true);
    if (!valid || submitting) return;
    onSubmit(phone);
  }

  return (
    <>
      <button className="back-link" onClick={onBack}>
        ← Choose a different plan
      </button>

      <div className="plan-recap">
        <div>
          <p className="plan-recap__name">{plan.name}</p>
          <p className="plan-recap__meta">{plan.speed_mbps} Mbps</p>
        </div>
        <div className="plan-recap__price">KES {plan.price_kes}</div>
      </div>

      <form onSubmit={handleSubmit}>
        <label className="field-label" htmlFor="phone">
          M-Pesa phone number
        </label>
        <input
          id="phone"
          className="phone-input"
          type="tel"
          inputMode="numeric"
          placeholder="07XX XXX XXX"
          value={phone}
          onChange={(e) => setPhone(e.target.value)}
          onBlur={() => setTouched(true)}
          autoFocus
        />
        {touched && !valid && (
          <p className="field-error">Enter a valid Safaricom number, e.g. 0712345678.</p>
        )}
        {!touched && <p className="field-hint">You'll get a prompt on this number to enter your PIN.</p>}
        {submitError && <p className="field-error">{submitError}</p>}

        <button className="primary-button" type="submit" disabled={submitting}>
          {submitting ? "Sending prompt…" : `Pay KES ${plan.price_kes}`}
        </button>
      </form>
    </>
  );
}
