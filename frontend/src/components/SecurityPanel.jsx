import { Lock, EyeOff, FolderLock, FileCheck2 } from "lucide-react";

const PROTECTIONS = [
  {
    icon: FolderLock,
    title: "Session Isolation",
    desc: "Every search is filtered to this browser's session ID. Other users' documents are structurally unreachable.",
  },
  {
    icon: EyeOff,
    title: "Sensitive Data Masking",
    desc: "Emails, phone numbers, passwords, client IDs, and other PII are redacted before context reaches the AI model.",
  },
  {
    icon: FileCheck2,
    title: "File Validation",
    desc: "Only PDF, DOCX, and TXT files are accepted, with a configurable size limit to prevent resource abuse.",
  },
  {
    icon: Lock,
    title: "Secure Storage",
    desc: "Uploaded files are saved under randomly generated names with path-traversal protection.",
  },
];

export default function SecurityPanel({ sessionId }) {
  return (
    <aside className="hidden w-[320px] shrink-0 flex-col border-l border-outline bg-surface p-5 lg:flex">
      <p className="mb-4 text-xs font-semibold uppercase tracking-wide text-on-surface-variant">
        Active Protections
      </p>
      <div className="space-y-4">
        {PROTECTIONS.map(({ icon: Icon, title, desc }) => (
          <div key={title} className="rounded-lg border border-outline p-3">
            <div className="mb-1.5 flex items-center gap-2">
              <div className="flex h-7 w-7 items-center justify-center rounded-md bg-emerald-container/10 text-emerald">
                <Icon size={14} />
              </div>
              <p className="text-sm font-semibold text-on-surface">{title}</p>
            </div>
            <p className="text-xs leading-relaxed text-on-surface-variant">{desc}</p>
          </div>
        ))}
      </div>

      {sessionId && (
        <div className="mt-auto pt-4">
          <p className="text-[11px] text-on-surface-variant">Session ID</p>
          <p className="truncate font-mono text-[11px] text-on-surface">{sessionId}</p>
        </div>
      )}
    </aside>
  );
}
