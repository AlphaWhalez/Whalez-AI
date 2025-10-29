
export async function reconcile(services) {
  const res = await fetch("/governance/reconcile", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(services),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function mintToken(subject, scopes = ["read:secrets"], ttlSeconds = 3600) {
  const res = await fetch("/security/auth/token", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ subject, scopes, ttl_s: ttlSeconds }),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function verifyToken(token) {
  const res = await fetch("/security/auth/verify", {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function setSecret(key, value, token) {
  const res = await fetch("/security/secrets/set", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({ key, value }),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function getSecret(key, token) {
  const res = await fetch(`/security/secrets/get?key=${encodeURIComponent(key)}`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}
