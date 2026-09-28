const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:5000";

async function request(path, options = {}) {
  let res;
  try {
    res = await fetch(`${API_BASE}${path}`, {
      headers: { "Content-Type": "application/json" },
      ...options,
    });
  } catch (networkErr) {
    throw new Error("Can't reach the server. Check your connection and try again.");
  }

  const data = await res.json().catch(() => ({}));

  if (!res.ok) {
    throw new Error(data.error || "Something went wrong. Please try again.");
  }
  return data;
}

export function getPlans() {
  return request("/api/plans");
}

export function createOrder(planId, phoneNumber) {
  return request("/api/orders", {
    method: "POST",
    body: JSON.stringify({ plan_id: planId, phone_number: phoneNumber }),
  });
}

export function getOrderStatus(orderId) {
  return request(`/api/orders/${orderId}/status`);
}

export function getOrder(orderId) {
  return request(`/api/orders/${orderId}`);
}
