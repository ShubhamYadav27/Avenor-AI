"use client";

import { useEffect, useMemo, useState } from "react";
import {
  Archive,
  Clipboard,
  Mail,
  RefreshCw,
  Send,
  Sparkles,
} from "lucide-react";
import {
  useArchiveEmail,
  useCompanyEmails,
  useCopyEmail,
  useGenerateEmails,
  useRegenerateEmail,
} from "@/hooks/use-api";
import { getErrorMessage } from "@/lib/api-client";
import { cn, timeAgo } from "@/lib/utils";
import { Skeleton } from "@/components/ui/skeleton";
import type {
  CompanyContact,
  EmailCTA,
  EmailLength,
  EmailResponse,
  EmailTone,
  EmailType,
  EmailVariation,
} from "@/types/api";

const EMAIL_TYPES: { value: EmailType; label: string }[] = [
  { value: "cold_email", label: "Cold Email" },
  { value: "follow_up_email", label: "Follow-up" },
  { value: "re_engagement_email", label: "Re-engagement" },
  { value: "meeting_request", label: "Meeting Request" },
  { value: "product_demo_invitation", label: "Demo Invite" },
  { value: "value_proposition_email", label: "Value Prop" },
];

const TONES: { value: EmailTone; label: string }[] = [
  { value: "professional", label: "Professional" },
  { value: "friendly", label: "Friendly" },
  { value: "executive", label: "Executive" },
  { value: "technical", label: "Technical" },
  { value: "consultative", label: "Consultative" },
];

const LENGTHS: { value: EmailLength; label: string }[] = [
  { value: "short", label: "Short" },
  { value: "medium", label: "Medium" },
  { value: "long", label: "Long" },
];

const CTAS: { value: EmailCTA; label: string }[] = [
  { value: "book_meeting", label: "Book Meeting" },
  { value: "demo", label: "Demo" },
  { value: "quick_call", label: "Quick Call" },
  { value: "reply", label: "Reply" },
  { value: "learn_more", label: "Learn More" },
];

const VARIATIONS: EmailVariation[] = ["A", "B", "C"];

function SelectField<T extends string>({
  label,
  value,
  options,
  onChange,
}: {
  label: string;
  value: T;
  options: { value: T; label: string }[];
  onChange: (value: T) => void;
}) {
  return (
    <label className="block min-w-0">
      <span className="mb-1 block text-xs font-semibold text-slate-700 dark:text-slate-300">{label}</span>
      <select
        value={value}
        onChange={(event) => onChange(event.target.value as T)}
        className="h-9 w-full rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-950 px-3 text-xs font-semibold text-slate-900 dark:text-white outline-none transition-colors focus:border-indigo-500 shadow-2xs"
      >
        {options.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
    </label>
  );
}

function ProgressState() {
  const [stage, setStage] = useState(0);
  const stages = ["Preparing research context", "Writing variations", "Checking structure"];

  useEffect(() => {
    const timer = setInterval(() => setStage((s) => Math.min(s + 1, stages.length - 1)), 2200);
    return () => clearInterval(timer);
  }, [stages.length]);

  return (
    <div className="rounded-xl border border-indigo-200 dark:border-indigo-500/30 bg-indigo-50/50 dark:bg-indigo-500/10 p-4">
      <div className="mb-3 flex items-center gap-2 text-sm font-semibold text-indigo-900 dark:text-indigo-400">
        <RefreshCw className="h-4 w-4 animate-spin text-indigo-600 dark:text-indigo-400 motion-reduce:animate-none" />
        {stages[stage]}
      </div>
      <div className="h-1.5 overflow-hidden rounded-full bg-slate-200 dark:bg-slate-700">
        <div
          className="h-full rounded-full bg-indigo-600 transition-all duration-700"
          style={{ width: `${((stage + 1) / stages.length) * 100}%` }}
        />
      </div>
    </div>
  );
}

function EmailDraft({
  email,
  selected,
  onCopy,
  onRegenerate,
  onArchive,
  busy,
}: {
  email: EmailResponse;
  selected: boolean;
  onCopy: (subject: string, body: string, cta: string) => void;
  onRegenerate: () => void;
  onArchive: () => void;
  busy: boolean;
}) {
  const [subject, setSubject] = useState(email.subject ?? "");
  const [body, setBody] = useState(email.body ?? "");
  const [cta, setCta] = useState(email.cta ?? "");

  if (!selected) return null;

  if (email.status === "failed") {
    return (
      <div className="rounded-xl border border-red-200 dark:border-red-500/30 bg-red-50 dark:bg-red-500/10 p-4">
        <p className="text-sm font-bold text-red-900 dark:text-red-400">Variation {email.variation} Failed</p>
        <p className="mt-1 text-xs font-medium text-red-700 dark:text-red-400">
          {email.error_message ?? "The email could not be generated."}
        </p>
        <button
          type="button"
          onClick={onRegenerate}
          disabled={busy}
          className="mt-3 inline-flex items-center gap-1.5 rounded-xl bg-red-600 px-3.5 py-1.5 text-xs font-semibold text-white hover:bg-red-700 disabled:opacity-60 shadow-2xs"
        >
          <RefreshCw className={cn("h-3.5 w-3.5", busy && "animate-spin")} />
          Retry Variation
        </button>
      </div>
    );
  }

  const pending = email.status === "pending" || email.status === "running";

  return (
    <div className="space-y-3.5 rounded-2xl border border-slate-200/60 dark:border-slate-700/50 bg-white dark:bg-slate-900/60 p-4 shadow-xs">
      {pending ? (
        <div className="space-y-2">
          <Skeleton className="h-9 w-full" />
          <Skeleton className="h-28 w-full" />
        </div>
      ) : (
        <>
          <label className="block">
            <span className="mb-1 block text-xs font-semibold text-slate-700 dark:text-slate-300">Subject</span>
            <input
              value={subject}
              onChange={(event) => setSubject(event.target.value)}
              className="h-9 w-full rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-950 px-3 text-sm font-semibold text-slate-900 dark:text-white outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-100 dark:focus:ring-indigo-500/30 placeholder:text-slate-400 dark:placeholder:text-slate-500"
            />
          </label>
          <label className="block">
            <span className="mb-1 block text-xs font-semibold text-slate-700 dark:text-slate-300">Body</span>
            <textarea
              value={body}
              onChange={(event) => setBody(event.target.value)}
              rows={9}
              className="w-full resize-y rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-950 px-3 py-2 text-sm leading-relaxed text-slate-800 dark:text-slate-200 outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-100 dark:focus:ring-indigo-500/30 placeholder:text-slate-400 dark:placeholder:text-slate-500"
            />
          </label>
          <label className="block">
            <span className="mb-1 block text-xs font-semibold text-slate-700 dark:text-slate-300">CTA</span>
            <input
              value={cta}
              onChange={(event) => setCta(event.target.value)}
              className="h-9 w-full rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-950 px-3 text-sm text-slate-800 dark:text-slate-200 outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-100 dark:focus:ring-indigo-500/30 placeholder:text-slate-400 dark:placeholder:text-slate-500"
            />
          </label>
          {email.reasoning && (
            <details className="rounded-xl border border-slate-200/80 dark:border-slate-700/60 bg-slate-50/80 dark:bg-slate-800/40 p-3">
              <summary className="cursor-pointer text-xs font-bold text-slate-700 dark:text-slate-300">
                Why this email was generated
              </summary>
              <p className="mt-2 text-xs leading-relaxed text-slate-600 dark:text-slate-300">{email.reasoning}</p>
            </details>
          )}
          <div className="flex flex-wrap items-center justify-between gap-2 pt-1">
            <p className="text-xs text-slate-500 dark:text-slate-400">
              v{email.version}
              {email.updated_at ? ` - ${timeAgo(email.updated_at)}` : ""}
              {email.copy_count ? ` - copied ${email.copy_count}x` : ""}
            </p>
            <div className="flex gap-2">
              <button
                type="button"
                onClick={() => onCopy(subject, body, cta)}
                className="inline-flex items-center gap-1.5 rounded-xl bg-indigo-600 px-3.5 py-1.5 text-xs font-semibold text-white hover:bg-indigo-700 shadow-xs cursor-pointer"
              >
                <Clipboard className="h-3.5 w-3.5" />
                Copy Draft
              </button>
              <button
                type="button"
                onClick={onRegenerate}
                disabled={busy}
                className="inline-flex items-center gap-1.5 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 px-3.5 py-1.5 text-xs font-semibold text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-700 disabled:opacity-60 shadow-2xs cursor-pointer"
              >
                <RefreshCw className={cn("h-3.5 w-3.5 text-indigo-600 dark:text-indigo-400", busy && "animate-spin")} />
                Regenerate
              </button>
              <button
                type="button"
                onClick={onArchive}
                className="inline-flex items-center gap-1.5 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 px-3.5 py-1.5 text-xs font-semibold text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-700 shadow-2xs cursor-pointer"
              >
                <Archive className="h-3.5 w-3.5" />
                Archive
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  );
}

export function EmailGeneratorPanel({
  companyId,
  contacts,
}: {
  companyId: string;
  contacts: CompanyContact[];
}) {
  const { data, isLoading, isError, error } = useCompanyEmails(companyId);
  const generate = useGenerateEmails(companyId);
  const copy = useCopyEmail(companyId);
  const regenerate = useRegenerateEmail(companyId);
  const archive = useArchiveEmail(companyId);

  const [contactId, setContactId] = useState<string>("none");
  const [emailType, setEmailType] = useState<EmailType>("cold_email");
  const [tone, setTone] = useState<EmailTone>("professional");
  const [length, setLength] = useState<EmailLength>("medium");
  const [ctaType, setCtaType] = useState<EmailCTA>("book_meeting");
  const [selectedVariation, setSelectedVariation] = useState<EmailVariation>("A");
  const [copiedId, setCopiedId] = useState<string | null>(null);

  const latestByVariation = useMemo(() => {
    const map = new Map<EmailVariation, EmailResponse>();
    for (const email of data?.emails ?? []) {
      const existing = map.get(email.variation);
      if (!existing || email.version > existing.version) map.set(email.variation, email);
    }
    return map;
  }, [data?.emails]);

  const selectedEmail = latestByVariation.get(selectedVariation);
  const generating = data?.status === "pending" || data?.status === "running" || generate.isPending;

  const runGenerate = (force_refresh = false) => {
    generate.mutate({
      email_type: emailType,
      tone,
      length,
      cta_type: ctaType,
      contact_id: contactId === "none" ? null : contactId,
      force_refresh,
    });
  };

  const copyDraft = async (email: EmailResponse, subject: string, body: string, cta: string) => {
    const text = `Subject: ${subject}\n\n${body}\n\n${cta}`;
    await navigator.clipboard.writeText(text);
    copy.mutate(email.id);
    setCopiedId(email.id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  return (
    <div className="rounded-2xl border border-slate-200/90 dark:border-slate-800/80 bg-white dark:bg-slate-900/90 p-5 shadow-xs">
      <div className="mb-4 flex flex-wrap items-start justify-between gap-3">
        <div className="min-w-0">
          <h3 className="flex items-center gap-2 text-sm font-bold text-slate-900 dark:text-white">
            <Mail className="h-4 w-4 text-indigo-600 dark:text-indigo-400" />
            AI Email Outreach Generator
          </h3>
          <p className="mt-1 text-xs leading-relaxed text-slate-500 dark:text-slate-400">
            Generate SDR-ready signal outreach from the latest AI research.
          </p>
        </div>
        <button
          type="button"
          onClick={() => runGenerate(false)}
          disabled={generate.isPending || generating}
          className="inline-flex items-center gap-1.5 rounded-xl bg-indigo-600 px-3.5 py-2 text-xs font-semibold text-white hover:bg-indigo-700 disabled:cursor-not-allowed disabled:opacity-60 shadow-xs cursor-pointer"
        >
          {generate.isPending || generating ? (
            <RefreshCw className="h-3.5 w-3.5 animate-spin motion-reduce:animate-none" />
          ) : (
            <Sparkles className="h-3.5 w-3.5" />
          )}
          Generate Outreach
        </button>
      </div>

      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        <label className="block min-w-0">
          <span className="mb-1 block text-xs font-semibold text-slate-700 dark:text-slate-300">Contact</span>
          <select
            value={contactId}
            onChange={(event) => setContactId(event.target.value)}
            className="h-9 w-full rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-950 px-3 text-xs font-semibold text-slate-900 dark:text-white outline-none focus:border-indigo-500 shadow-2xs"
          >
            <option value="none">No specific contact</option>
            {contacts.map((contact) => (
              <option key={contact.id} value={contact.id}>
                {contact.name ?? contact.email ?? "Unknown contact"}
                {contact.title ? `, ${contact.title}` : ""}
              </option>
            ))}
          </select>
        </label>
        <SelectField label="Email Type" value={emailType} options={EMAIL_TYPES} onChange={setEmailType} />
        <SelectField label="Tone" value={tone} options={TONES} onChange={setTone} />
        <SelectField label="Length" value={length} options={LENGTHS} onChange={setLength} />
        <SelectField label="CTA" value={ctaType} options={CTAS} onChange={setCtaType} />
      </div>

      <div className="mt-4 space-y-3">
        {isLoading && (
          <div className="space-y-2">
            <Skeleton className="h-10 w-full" />
            <Skeleton className="h-40 w-full" />
          </div>
        )}

        {(isError || generate.isError) && (
          <div className="rounded-xl border border-red-200 dark:border-red-500/30 bg-red-50 dark:bg-red-500/10 p-4 text-xs font-semibold text-red-700 dark:text-red-400">
            {getErrorMessage(error ?? generate.error)}
          </div>
        )}

        {generating && <ProgressState />}

        {!generating && data?.status === "failed" && (
          <div className="rounded-xl border border-red-200 dark:border-red-500/30 bg-red-50 dark:bg-red-500/10 p-4 text-xs font-semibold text-red-700 dark:text-red-400">
            {data.error_message ?? "Email generation failed."}
          </div>
        )}

        {!generating && latestByVariation.size > 0 && (
          <>
            <div className="flex flex-wrap gap-2">
              {VARIATIONS.map((variation) => {
                const email = latestByVariation.get(variation);
                return (
                  <button
                    type="button"
                    key={variation}
                    onClick={() => setSelectedVariation(variation)}
                    className={cn(
                      "inline-flex h-8 items-center gap-1.5 rounded-xl border px-3 text-xs font-semibold transition-all cursor-pointer",
                      selectedVariation === variation
                        ? "border-indigo-200 dark:border-indigo-500/30 bg-indigo-50 dark:bg-indigo-500/10 text-indigo-700 dark:text-indigo-400 font-bold shadow-2xs"
                        : "border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-600 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-700"
                    )}
                  >
                    Variation {variation}
                    {email?.status === "completed" && <Send className="h-3 w-3 text-indigo-600 dark:text-indigo-400" />}
                    {email?.status === "failed" && <span className="text-red-500 font-bold">!</span>}
                  </button>
                );
              })}
            </div>

            {selectedEmail && (
              <>
                {copiedId === selectedEmail.id && (
                  <div className="rounded-xl border border-emerald-200 dark:border-emerald-500/30 bg-emerald-50 dark:bg-emerald-500/10 px-3.5 py-2 text-xs font-semibold text-emerald-800 dark:text-emerald-400">
                    Copied editable draft to clipboard.
                  </div>
                )}
                <EmailDraft
                  key={selectedEmail.id}
                  email={selectedEmail}
                  selected
                  busy={regenerate.isPending}
                  onCopy={(subject, body, cta) => copyDraft(selectedEmail, subject, body, cta)}
                  onRegenerate={() => regenerate.mutate(selectedEmail.id)}
                  onArchive={() => archive.mutate(selectedEmail.id)}
                />
              </>
            )}
          </>
        )}

        {!isLoading && !generating && latestByVariation.size === 0 && !isError && (
          <div className="rounded-2xl border border-dashed border-slate-300 dark:border-slate-700/60 bg-slate-50/70 dark:bg-slate-800/40 p-6 text-center">
            <p className="text-sm font-bold text-slate-900 dark:text-white">No Emails Generated Yet</p>
            <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">
              Choose a recipient and template, then generate three variations.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
