"use client";

import Image from "next/image";
import { ChangeEvent, FormEvent, useCallback, useEffect, useRef, useState } from "react";
import { api, download, Expense, formatMoney, identities, ReceiptUpload } from "@/lib/api";

type RoleName = keyof typeof identities;
type Metrics = Record<string, number | string | null>;

export default function Home() {
  const [role, setRole] = useState<RoleName>("Employee");
  const [expenses, setExpenses] = useState<Expense[]>([]);
  const [receipt, setReceipt] = useState<ReceiptUpload | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [draft, setDraft] = useState({ merchant: "", amount: "", date: "" });
  const [audit, setAudit] = useState<{ chain_valid: boolean; events: Array<Record<string, unknown>> } | null>(null);
  const [metrics, setMetrics] = useState<Metrics | null>(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const identity = identities[role];
  const reviewStartedAt = useRef(0);

  const refresh = useCallback(async () => {
    setError("");
    try {
      setExpenses(await api<Expense[]>("/expenses", identity));
      reviewStartedAt.current = Date.now();
      if (role === "Admin" || role === "Auditor") {
        setAudit(await api("/audit-events", identity));
        setMetrics(await api("/metrics/product", identity));
      } else {
        setAudit(null);
        setMetrics(null);
      }
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Unable to load data");
    }
  }, [identity, role]);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    void refresh();
  }, [refresh]);

  async function upload(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (!file) return;
    setBusy(true);
    setError("");
    try {
      const body = new FormData();
      body.append("file", file);
      const uploaded = await api<ReceiptUpload>("/receipts", identity, { method: "POST", body });
      setReceipt(uploaded);
      if (uploaded.scan_status === "CLEAN") {
        setPreview(URL.createObjectURL(file));
        setDraft({ merchant: uploaded.extracted_merchant ?? "", amount: uploaded.extracted_amount_minor ? String(uploaded.extracted_amount_minor / 100) : "", date: uploaded.extracted_date ?? "" });
      } else {
        setPreview(null);
        setDraft({ merchant: "", amount: "", date: "" });
        setError(`Receipt blocked: ${uploaded.scan_result ?? uploaded.scan_status}`);
      }
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Receipt upload failed");
    } finally { setBusy(false); }
  }

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!receipt || receipt.scan_status !== "CLEAN") return setError("Upload a receipt that passes security scanning before submitting the claim");
    const form = event.currentTarget;
    const data = new FormData(form);
    setBusy(true); setError("");
    try {
      await api("/expenses", identity, { method: "POST", headers: { "Idempotency-Key": crypto.randomUUID() }, body: JSON.stringify({ merchant: draft.merchant, amount_minor: Math.round(Number(draft.amount) * 100), currency: "INR", incurred_date: draft.date, category: data.get("category"), purpose: data.get("purpose"), receipt_id: receipt.id }) });
      form.reset(); setReceipt(null); setPreview(null); setDraft({ merchant: "", amount: "", date: "" }); await refresh();
    } catch (cause) { setError(cause instanceof Error ? cause.message : "Submission failed"); }
    finally { setBusy(false); }
  }

  async function decide(expense: Expense, action: "APPROVE" | "REJECT" | "REQUEST_INFORMATION") {
    let reason = ""; let requested_fields: string[] = [];
    if (action === "REQUEST_INFORMATION") {
      reason = window.prompt("Message to employee:", "Please provide the missing receipt details.") ?? "";
      const fields = window.prompt("Requested fields: purpose, receipt, or purpose,receipt", "receipt") ?? "";
      requested_fields = fields.split(",").map((item) => item.trim()).filter((item) => item === "purpose" || item === "receipt");
    } else if (action !== "APPROVE" || expense.recommendation !== "APPROVE_RECOMMENDED") {
      reason = window.prompt("Reason required for rejection or recommendation override:") ?? "";
    }
    setBusy(true);
    try {
      await api(`/expenses/${expense.id}/decisions`, identity, { method: "POST", headers: { "Idempotency-Key": crypto.randomUUID() }, body: JSON.stringify({ action, reason, requested_fields, expected_row_version: expense.row_version, reviewer_active_ms: Date.now() - reviewStartedAt.current }) });
      await refresh();
    } catch (cause) { setError(cause instanceof Error ? cause.message : "Decision failed"); }
    finally { setBusy(false); }
  }

  async function resubmit(expense: Expense) {
    const purpose = window.prompt("Updated business purpose:", expense.purpose);
    if (!purpose) return;
    const receiptWasRequested = expense.requested_fields.includes("receipt");
    if (receiptWasRequested && (!receipt || receipt.id === expense.receipt_id)) {
      setError("Upload the requested replacement receipt above before resubmitting");
      return;
    }
    setBusy(true);
    try {
      await api(`/expenses/${expense.id}/resubmissions`, identity, { method: "POST", body: JSON.stringify({ purpose, receipt_id: receiptWasRequested ? receipt?.id : expense.receipt_id }) });
      if (receiptWasRequested) { setReceipt(null); setPreview(null); setDraft({ merchant: "", amount: "", date: "" }); }
      await refresh();
    }
    catch (cause) { setError(cause instanceof Error ? cause.message : "Resubmission failed"); }
    finally { setBusy(false); }
  }

  async function exportCsv(expense: Expense) {
    const account_code = window.prompt("Confirmed account code:", "TRAVEL") ?? "";
    const cost_center = window.prompt("Confirmed cost center:", "INDIA-SALES") ?? "";
    if (!account_code || !cost_center) return;
    setBusy(true);
    try {
      const result = await api<{ download_url: string }>(`/expenses/${expense.id}/exports`, identity, { method: "POST", body: JSON.stringify({ account_code, cost_center, expected_row_version: expense.row_version }) });
      const blob = await download(result.download_url, identity);
      const link = document.createElement("a"); link.href = URL.createObjectURL(blob); link.download = `clears-spend-${expense.id}.csv`; link.click(); URL.revokeObjectURL(link.href); await refresh();
    } catch (cause) {
      const message = cause instanceof Error ? cause.message : "Export failed";
      await refresh();
      setError(message);
    }
    finally { setBusy(false); }
  }

  return <main>
    <header className="topbar"><div className="brand"><span className="mark">C</span><div><strong>ClearSpend</strong><small>Receipt-to-accounting evidence</small></div></div><label className="role">View as<select value={role} onChange={(event) => setRole(event.target.value as RoleName)}>{Object.keys(identities).map((name) => <option key={name}>{name}</option>)}</select></label></header>
    <section className="hero"><div><p className="eyebrow">REIMBURSEMENT CONTROL CENTER</p><h1>From receipt to books,<br /><em>clear and accountable.</em></h1><p>Receipt extraction, deterministic policy checks, bounded AI assistance, human authority, and an accountant-ready handoff.</p></div><div className="trust"><span>● System operational</span><strong>{expenses.filter((e) => e.state === "AWAITING_REVIEW").length}</strong><small>awaiting review</small></div></section>
    {error && <div className="alert" role="alert">{error}</div>}
    {role === "Employee" && <section className="panel"><div className="panelTitle"><div><p className="eyebrow">RECEIPT FIRST</p><h2>Start with evidence</h2></div><span className="step">1 Scan · 2 Verify · 3 Submit</span></div><div className="receiptGrid"><label className="dropzone"><strong>Upload receipt</strong><span>JPEG, PNG, or PDF · maximum 5 MB · malware scanned</span><input type="file" accept="image/jpeg,image/png,application/pdf" onChange={(event) => void upload(event)} disabled={busy} /></label><div className="preview">{preview ? (receipt?.content_type === "application/pdf" ? <object data={preview} type="application/pdf">PDF receipt selected</object> : <Image src={preview} alt="Receipt preview" width={700} height={240} unoptimized />) : <span>Preview available after security scan</span>}</div></div>{receipt && <div className={`extraction ${receipt.extraction_status.toLowerCase()}`}><strong>{receipt.scan_status === "CLEAN" ? (receipt.extraction_status === "EXTRACTED" ? "Security scan passed—verify extracted fields" : "Security scan passed—enter unreadable fields manually") : `Receipt blocked: ${receipt.scan_status}`}</strong><span>{receipt.security_flags.length > 0 ? `Security flags: ${receipt.security_flags.join(", ")}` : "Encrypted storage · signature validation · malware scan"}</span></div>}<form onSubmit={submit} className="formGrid"><label>Merchant<input required disabled={receipt?.scan_status !== "CLEAN"} value={draft.merchant} onChange={(e) => setDraft({ ...draft, merchant: e.target.value })} /></label><label>Amount (INR)<input required disabled={receipt?.scan_status !== "CLEAN"} min="0.01" step="0.01" type="number" value={draft.amount} onChange={(e) => setDraft({ ...draft, amount: e.target.value })} /></label><label>Incurred date<input required disabled={receipt?.scan_status !== "CLEAN"} type="date" value={draft.date} onChange={(e) => setDraft({ ...draft, date: e.target.value })} /></label><label>Category<select name="category" disabled={receipt?.scan_status !== "CLEAN"}><option>travel</option><option>meals</option><option>office</option><option>alcohol</option><option>personal</option></select></label><label className="wide">Business purpose<textarea name="purpose" required disabled={receipt?.scan_status !== "CLEAN"} placeholder="Who, why, and expected business outcome" /></label><button disabled={busy || receipt?.scan_status !== "CLEAN"} type="submit">{busy ? "Working…" : "Submit for assessment →"}</button></form></section>}
    <section className="panel"><div className="panelTitle"><div><p className="eyebrow">{role === "Reviewer" ? "REVIEW QUEUE" : "CLAIMS"}</p><h2>{role === "Reviewer" ? "Decisions that need you" : "Expense activity"}</h2></div><button className="secondary" onClick={() => void refresh()}>Refresh</button></div><div className="cards">{expenses.length === 0 && <p className="empty">No claims visible for this identity.</p>}{expenses.map((expense) => <article className="claim" key={expense.id}><div className="claimHead"><div><strong>{expense.merchant}</strong><small>{expense.category} · {expense.incurred_date}</small></div><strong>{formatMoney(expense.amount_minor, expense.currency)}</strong></div><div className="badges"><span className={`state ${expense.state.toLowerCase()}`}>{expense.state.replaceAll("_", " ")}</span>{expense.recommendation && <span className="recommendation">Recommendation—not decision: {expense.recommendation.replaceAll("_", " ")}</span>}</div><p>{expense.purpose}</p>{expense.receipt && <a className="receiptLink" href="#" onClick={async (event) => { event.preventDefault(); const blob = await download(`/api/v1/receipts/${expense.receipt_id}/content`, identity); window.open(URL.createObjectURL(blob)); }}>View current receipt · {expense.receipt.scan_status.toLowerCase()}</a>}{expense.receipt_history.length > 0 && <details className="checks"><summary>Receipt audit history · {expense.receipt_history.length} version{expense.receipt_history.length === 1 ? "" : "s"}</summary>{expense.receipt_history.map((item) => <div className="checkRow" key={item.version_id}><span className={item.scan_status === "CLEAN" ? "pass" : "unknown"}>R{item.revision}</span><p><strong>{item.attachment_type.replaceAll("_", " ")}{item.is_current ? " · current" : " · superseded"}</strong><br />{item.filename} · {item.scan_status.toLowerCase()} · hash {item.content_hash.slice(0, 12)}…</p></div>)}</details>}{expense.information_request_message && <div className="infoRequest"><strong>Finance requested: {expense.requested_fields.join(", ")}</strong><p>{expense.information_request_message}</p></div>}{expense.checks.length > 0 && <div className="checks"><strong>{expense.checks.length} evidence checks</strong>{expense.checks.map((check) => <div className="checkRow" key={check.check_key}><span className={check.status.toLowerCase()}>{check.status}</span><p><strong>{check.source} · {check.reason_code.replaceAll("_", " ")}</strong><br />{check.explanation}</p></div>)}</div>}{expense.policy_citations.map((citation) => <blockquote key={citation.id}><strong>{citation.title}</strong><span>{citation.text}</span></blockquote>)}{(role === "Reviewer" || role === "Admin") && expense.state === "AWAITING_REVIEW" && <div className="actions"><button disabled={busy} onClick={() => void decide(expense, "APPROVE")}>Approve</button><button className="danger" disabled={busy} onClick={() => void decide(expense, "REJECT")}>Reject</button><button className="secondary" disabled={busy} onClick={() => void decide(expense, "REQUEST_INFORMATION")}>Request info</button></div>}{role === "Employee" && expense.state === "INFORMATION_REQUESTED" && <div className="actions"><button disabled={busy} onClick={() => void resubmit(expense)}>Update and resubmit</button></div>}{(role === "Reviewer" || role === "Admin") && (expense.state === "READY_TO_EXPORT" || expense.state === "EXPORT_FAILED") && <div className="handoff"><strong>Human-confirmed accounting handoff</strong><p>Confirm coding, then download an accountant-ready CSV. This does not move money.</p><button disabled={busy} onClick={() => void exportCsv(expense)}>Confirm coding & export CSV</button></div>}{expense.export?.status === "EXPORTED" && <div className="verified">✓ Exported to accountant-ready CSV</div>}</article>)}</div></section>
    {metrics && <section className="panel"><div className="panelTitle"><div><p className="eyebrow">OPERATING SIGNALS</p><h2>What the system can prove</h2></div><span className="step">Not payment evidence</span></div><div className="metricGrid">{Object.entries(metrics).filter(([key]) => key !== "note").map(([key, value]) => <div key={key}><strong>{value === null ? "—" : typeof value === "number" ? Math.round(value * 100) / 100 : value}</strong><span>{key.replaceAll("_", " ")}</span></div>)}</div><p className="empty">{String(metrics.note)}</p></section>}
    {audit && <section className="panel"><div className="panelTitle"><div><p className="eyebrow">AUDIT EVIDENCE</p><h2>Hash-linked event trail</h2></div><span className={audit.chain_valid ? "verified" : "invalid"}>{audit.chain_valid ? "✓ Chain verified" : "! Chain invalid"}</span></div><div className="timeline">{audit.events.map((event) => <div key={String(event.id)}><span>{String(event.sequence).padStart(2, "0")}</span><p><strong>{String(event.action)}</strong><small>{String(event.entity_type)} · {String(event.correlation_id).slice(0, 16)}…</small></p></div>)}</div></section>}
  </main>;
}
