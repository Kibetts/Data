// Renders bandwidth as bars instead of a generic icon — bar count scales
// with speed relative to the fastest plan on offer, so the graphic itself
// carries the comparison instead of decorating it.
const BAR_COUNT = 6;

export default function SignalMeter({ speedMbps, maxSpeed, pulsing = false }) {
  const filled = pulsing
    ? BAR_COUNT
    : Math.max(1, Math.round((speedMbps / maxSpeed) * BAR_COUNT));

  return (
    <div className={`signal-meter${pulsing ? " is-pulsing" : ""}`} aria-hidden="true">
      {Array.from({ length: BAR_COUNT }).map((_, i) => (
        <span
          key={i}
          className={`signal-bar${i < filled ? " is-filled" : ""}`}
          style={{ height: `${10 + i * 4}px` }}
        />
      ))}
    </div>
  );
}
