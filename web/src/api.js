
export async function reconcile(services) {
  const res = await fetch("/governance/reconcile", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(services),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}
