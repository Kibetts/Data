import { useEffect, useRef, useState } from "react";
import { getPlans, createOrder, getOrderStatus, getOrder } from "./api.js";
import { BRAND_NAME, TAGLINE, POLL_INTERVAL_MS, POLL_TIMEOUT_MS } from "./constants.js";
import PlanList from "./components/PlanList.jsx";
import PhoneForm from "./components/PhoneForm.jsx";
import ProcessingScreen from "./components/ProcessingScreen.jsx";
import SuccessScreen from "./components/SuccessScreen.jsx";
import FailedScreen from "./components/FailedScreen.jsx";

// screen: "plans" | "phone" | "processing" | "success" | "failed"

export default function App() {
  const [screen, setScreen] = useState("plans");

  const [plans, setPlans] = useState([]);
  const [plansLoading, setPlansLoading] = useState(true);
  const [plansError, setPlansError] = useState(null);

  const [selectedPlan, setSelectedPlan] = useState(null);

  const [submitting, setSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState(null);
  const [phoneUsed, setPhoneUsed] = useState("");

  const [orderId, setOrderId] = useState(null);
  const [pollTimedOut, setPollTimedOut] = useState(false);
  const [finalOrder, setFinalOrder] = useState(null); // full order detail once paid/failed

  const pollHandle = useRef(null);
  const pollStartedAt = useRef(null);

  useEffect(() => {
    loadPlans();
  }, []);

  useEffect(() => {
    if (screen !== "processing" || !orderId) return;

    pollStartedAt.current = Date.now();
    setPollTimedOut(false);

    pollHandle.current = setInterval(async () => {
      if (Date.now() - pollStartedAt.current > POLL_TIMEOUT_MS) {
        clearInterval(pollHandle.current);
        setPollTimedOut(true);
        return;
      }
      await checkStatusOnce();
    }, POLL_INTERVAL_MS);

    return () => clearInterval(pollHandle.current);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [screen, orderId]);

  async function loadPlans() {
    setPlansLoading(true);
    setPlansError(null);
    try {
      const data = await getPlans();
      setPlans(data);
    } catch (err) {
      setPlansError(err.message);
    } finally {
      setPlansLoading(false);
    }
  }

  async function checkStatusOnce() {
    try {
      const status = await getOrderStatus(orderId);
      if (status.status === "paid" || status.status === "failed") {
        clearInterval(pollHandle.current);
        const full = await getOrder(orderId);
        setFinalOrder(full);
        setScreen(status.status === "paid" ? "success" : "failed");
      }
    } catch {
      // A single failed poll isn't fatal — the interval just tries again.
    }
  }

  function handleSelectPlan(plan) {
    setSelectedPlan(plan);
    setSubmitError(null);
    setScreen("phone");
  }

  async function handleSubmitPhone(phone) {
    setSubmitting(true);
    setSubmitError(null);
    try {
      const result = await createOrder(selectedPlan.id, phone);
      setOrderId(result.order_id);
      setPhoneUsed(phone);
      setFinalOrder(null);
      setScreen("processing");
    } catch (err) {
      setSubmitError(err.message);
    } finally {
      setSubmitting(false);
    }
  }

  function handleCancelProcessing() {
    clearInterval(pollHandle.current);
    setOrderId(null);
    setScreen("phone");
  }

  function handleRetryAfterFailure() {
    setScreen("phone");
  }

  function handleStartOver() {
    clearInterval(pollHandle.current);
    setSelectedPlan(null);
    setOrderId(null);
    setFinalOrder(null);
    setSubmitError(null);
    setScreen("plans");
  }

  return (
    <div className="screen">
      {screen === "plans" && (
        <>
          <header className="header">
            <p className="brand">{BRAND_NAME}</p>
            <h1 className="tagline">{TAGLINE}</h1>
          </header>
          <PlanList
            plans={plans}
            loading={plansLoading}
            error={plansError}
            onSelect={handleSelectPlan}
            onRetry={loadPlans}
          />
        </>
      )}

      {screen === "phone" && selectedPlan && (
        <PhoneForm
          plan={selectedPlan}
          submitting={submitting}
          submitError={submitError}
          onSubmit={handleSubmitPhone}
          onBack={() => setScreen("plans")}
        />
      )}

      {screen === "processing" && (
        <ProcessingScreen
          phone={phoneUsed}
          timedOut={pollTimedOut}
          onCheckAgain={checkStatusOnce}
          onCancel={handleCancelProcessing}
        />
      )}

      {screen === "success" && finalOrder && (
        <SuccessScreen order={finalOrder} onStartOver={handleStartOver} />
      )}

      {screen === "failed" && (
        <FailedScreen
          reason={finalOrder?.result_desc}
          onRetry={handleRetryAfterFailure}
          onStartOver={handleStartOver}
        />
      )}
    </div>
  );
}
