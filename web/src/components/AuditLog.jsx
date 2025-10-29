
export default function AuditLog({ events=[] }) {
  return (
    <div className="p-3 rounded-xl border mt-4">
      <div className="font-medium mb-2">Audit Log</div>
      <ul className="space-y-1 text-xs">
        {events.map((e,i)=>(<li key={i}><code>{JSON.stringify(e)}</code></li>))}
      </ul>
    </div>
  );
}
