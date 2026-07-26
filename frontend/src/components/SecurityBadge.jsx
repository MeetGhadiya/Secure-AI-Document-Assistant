import { ShieldCheck } from "lucide-react";

export default function SecurityBadge({ label = "Encrypted" }) {
  return (
    <span className="inline-flex items-center gap-1 rounded-full bg-emerald-container/10 px-2.5 py-1 text-[11px] font-semibold tracking-wide text-emerald">
      <ShieldCheck size={12} strokeWidth={2.5} />
      {label}
    </span>
  );
}
