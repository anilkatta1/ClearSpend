"use client";

import Image from "next/image";
import { ChangeEvent, FormEvent, useCallback, useEffect, useRef, useState } from "react";
import { api, download, Expense, formatMoney, identities, ReceiptUpload } from "@/lib/api";

type RoleName = keyof typeof identities;
type Metrics = Record<string, number | string | null>;
type ReceiptDraft = {
  receipt: ReceiptUpload;
  preview: string;
  merchant: string;
  amount: string;
  date: string;
};

export default function Home() {
  const [role, setRole] = useState<RoleName>("Employee");
  const [expenses, setExpenses] = useState<Expense[]>([]);
  const [receiptItems, setReceiptItems] = useState<ReceiptDraft[]>([]);
  const [supplementItems, setSupplementItems] = useState<Record<string, ReceiptDraft[]>>({});
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

  async function upload(event: ChangeEvent<HTMLInputElement>, expense?: Expense) {
    const selectedFiles = Array.from(event.target.files ?? []);
    const stagedItems = expense ? (supplementItems[expense.id] ?? []) : receiptItems;
    const existingReceiptCount = expense?.receipt_items.length ?? 0;
    const remainingCapacity = 20 - existingReceiptCount - stagedItems.length;
    if (selectedFiles.length === 0) return;
    if (remainingCapacity <= 0) {
      setError("A report may contain at most 20 receipts");
      event.target.value = "";
      return;
    }
    const files = selectedFiles.slice(0, remainingCapacity);
    const omittedCount = selectedFiles.length - files.length;
    setBusy(true);
    setError("");
    try {
      const outcomes = await Promise.allSettled(files.map(async (file) => {
        const body = new FormData();
        body.append("file", file);
        const receipt = await api<ReceiptUpload>("/receipts", identity, { method: "POST", body });
        return { receipt, file };
      }));
      const uploadedItems = outcomes.flatMap((outcome) => outcome.status === "fulfilled" ? [outcome.value] : []);
      const failedFiles = outcomes.flatMap((outcome, index) => outcome.status === "rejected" ? [`${files[index].name}: ${outcome.reason instanceof Error ? outcome.reason.message : "upload failed"}`] : []);
      const blocked = uploadedItems.filter(({ receipt }) => receipt.scan_status !== "CLEAN");
      const clean = uploadedItems.filter(({ receipt }) => receipt.scan_status === "CLEAN").map(({ receipt, file }) => ({
        receipt,
        preview: URL.createObjectURL(file),
        merchant: receipt.extracted_merchant ?? "",
        amount: receipt.extracted_amount_minor ? String(receipt.extracted_amount_minor / 100) : "",
        date: receipt.extracted_date ?? "",
      }));
      if (expense) {
        setSupplementItems((current) => ({
          ...current,
          [expense.id]: [...(current[expense.id] ?? []), ...clean],
        }));
      } else {
        setReceiptItems((current) => [...current, ...clean]);
      }
      const messages = [];
      if (omittedCount > 0) messages.push(`${omittedCount} file(s) exceeded the 20-receipt limit.`);
      if (failedFiles.length > 0) messages.push(`Upload failed—${failedFiles.join("; ")}. Successful uploads were preserved.`);
      if (blocked.length > 0) messages.push(`Security blocked—${blocked.map(({ receipt }) => `${receipt.filename}: ${receipt.scan_result ?? receipt.scan_status}`).join("; ")}.`);
      if (messages.length > 0) setError(messages.join(" "));
      event.target.value = "";
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Receipt upload failed");
    } finally { setBusy(false); }
  }

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (receiptItems.length === 0) return setError("Upload at least one clean receipt before submitting the report");
    const form = event.currentTarget;
    const data = new FormData(form);
    setBusy(true); setError("");
    try {
      await api("/expense-reports", identity, { method: "POST", headers: { "Idempotency-Key": crypto.randomUUID() }, body: JSON.stringify({ category: data.get("category"), purpose: data.get("purpose"), items: receiptItems.map((item) => ({ receipt_id: item.receipt.id, merchant: item.merchant, amount_minor: Math.round(Number(item.amount) * 100), currency: "INR", incurred_date: item.date })) }) });
      receiptItems.forEach((item) => URL.revokeObjectURL(item.preview));
      form.reset(); setReceiptItems([]); await refresh();
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
      // This runs only from a user click; the value measures active review time, not render state.
      // eslint-disable-next-line react-hooks/purity
      const reviewerActiveMs = Date.now() - reviewStartedAt.current;
      await api(`/expenses/${expense.id}/decisions`, identity, { method: "POST", headers: { "Idempotency-Key": crypto.randomUUID() }, body: JSON.stringify({ action, reason, requested_fields, expected_row_version: expense.row_version, reviewer_active_ms: reviewerActiveMs }) });
      await refresh();
    } catch (cause) { setError(cause instanceof Error ? cause.message : "Decision failed"); }
    finally { setBusy(false); }
  }

  async function resubmit(expense: Expense) {
    const purpose = window.prompt("Updated business purpose:", expense.purpose);
    if (!purpose) return;
    const receiptWasRequested = expense.requested_fields.includes("receipt");
    const requestedReceipts = supplementItems[expense.id] ?? [];
    if (receiptWasRequested && requestedReceipts.length === 0) {
      setError("Upload the requested receipt in this report's action-required panel before resubmitting");
      return;
    }
    setBusy(true);
    try {
      await api(`/expenses/${expense.id}/resubmissions`, identity, { method: "POST", body: JSON.stringify({ purpose, items: receiptWasRequested ? requestedReceipts.map((item) => ({ receipt_id: item.receipt.id, merchant: item.merchant, amount_minor: Math.round(Number(item.amount) * 100), currency: "INR", incurred_date: item.date })) : null, items_mode: "APPEND" }) });
      if (receiptWasRequested) {
        requestedReceipts.forEach((item) => URL.revokeObjectURL(item.preview));
        setSupplementItems((current) => {
          const next = { ...current };
          delete next[expense.id];
          return next;
        });
      }
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
    {role === "Employee" && (
      <section className="panel">
        <div className="panelTitle">
          <div>
            <p className="eyebrow">EXPENSE REPORT</p>
            <h2>Submit one trip as one approval</h2>
          </div>
          <span className="step">1 Scan · 2 Verify each line · 3 Submit</span>
        </div>
        <label className="dropzone compact">
          <strong>Upload up to 20 receipts</strong>
          <span>Choose multiple JPEG, PNG, or PDF files · 5 MB each · malware scanned before processing</span>
          <input
            type="file"
            multiple
            accept="image/jpeg,image/png,application/pdf"
            onChange={(event) => void upload(event)}
            disabled={busy || receiptItems.length >= 20}
          />
        </label>
        {receiptItems.length === 0 ? (
          <p className="empty">No clean receipts added yet.</p>
        ) : (
          <div className="receiptItems">
            {receiptItems.map((item, index) => (
              <article className="receiptEditor" key={item.receipt.id}>
                <div className="preview small">
                  {item.receipt.content_type === "application/pdf" ? (
                    <object data={item.preview} type="application/pdf">PDF receipt selected</object>
                  ) : (
                    <Image src={item.preview} alt={`Receipt ${index + 1} preview`} width={350} height={180} unoptimized />
                  )}
                </div>
                <div className="receiptMeta">
                  <div className="lineHeading">
                    <strong>Receipt {index + 1}</strong>
                    <button
                      className="secondary"
                      type="button"
                      onClick={() => {
                        URL.revokeObjectURL(item.preview);
                        setReceiptItems((current) => current.filter((candidate) => candidate.receipt.id !== item.receipt.id));
                      }}
                    >
                      Remove
                    </button>
                  </div>
                  <small>{item.receipt.filename} · scan clean · encrypted storage</small>
                  <label>Merchant
                    <input
                      required
                      value={item.merchant}
                      onChange={(event) => setReceiptItems((current) => current.map((candidate) => candidate.receipt.id === item.receipt.id ? { ...candidate, merchant: event.target.value } : candidate))}
                    />
                  </label>
                  <label>Amount (INR)
                    <input
                      required
                      min="0.01"
                      step="0.01"
                      type="number"
                      value={item.amount}
                      onChange={(event) => setReceiptItems((current) => current.map((candidate) => candidate.receipt.id === item.receipt.id ? { ...candidate, amount: event.target.value } : candidate))}
                    />
                  </label>
                  <label>Incurred date
                    <input
                      required
                      type="date"
                      value={item.date}
                      onChange={(event) => setReceiptItems((current) => current.map((candidate) => candidate.receipt.id === item.receipt.id ? { ...candidate, date: event.target.value } : candidate))}
                    />
                  </label>
                </div>
              </article>
            ))}
          </div>
        )}
        <form onSubmit={submit} className="formGrid reportForm">
          <label>Shared category
            <select name="category">
              <option>travel</option><option>meals</option><option>office</option><option>alcohol</option><option>personal</option>
            </select>
          </label>
          <label>Report total
            <input readOnly value={formatMoney(receiptItems.reduce((sum, item) => sum + Math.round(Number(item.amount || 0) * 100), 0), "INR")} />
          </label>
          <label className="wide">Business purpose
            <textarea name="purpose" required placeholder="Trip, client, business objective, and relevant context" />
          </label>
          <button disabled={busy || receiptItems.length === 0} type="submit">
            {busy ? "Working…" : `Submit ${receiptItems.length} receipt${receiptItems.length === 1 ? "" : "s"} for one assessment →`}
          </button>
        </form>
      </section>
    )}
    {role === "Employee" && expenses.some((expense) => expense.state === "INFORMATION_REQUESTED") && (
      <section className="panel actionRequired">
        <div className="panelTitle">
          <div>
            <p className="eyebrow">ACTION REQUIRED</p>
            <h2>Complete requested information</h2>
          </div>
          <span className="step">Original receipts stay attached</span>
        </div>
        <div className="cards">
          {expenses.filter((expense) => expense.state === "INFORMATION_REQUESTED").map((expense) => {
            const requestedReceipts = supplementItems[expense.id] ?? [];
            const receiptWasRequested = expense.requested_fields.includes("receipt");
            return (
              <article className="claim supplement" key={`supplement-${expense.id}`}>
                <div className="claimHead">
                  <div>
                    <strong>{expense.merchant}</strong>
                    <small>{expense.receipt_items.length} existing receipt line{expense.receipt_items.length === 1 ? "" : "s"}</small>
                  </div>
                  <strong>{formatMoney(expense.amount_minor, expense.currency)}</strong>
                </div>
                <div className="infoRequest">
                  <strong>Finance requested: {expense.requested_fields.join(", ")}</strong>
                  <p>{expense.information_request_message}</p>
                </div>
                {receiptWasRequested && (
                  <>
                    <label className="dropzone compact supplementUpload">
                      <strong>Upload only the missing receipt(s)</strong>
                      <span>New clean files are appended; the {expense.receipt_items.length} original line{expense.receipt_items.length === 1 ? " is" : "s are"} preserved</span>
                      <input
                        type="file"
                        multiple
                        accept="image/jpeg,image/png,application/pdf"
                        onChange={(event) => void upload(event, expense)}
                        disabled={busy || expense.receipt_items.length + requestedReceipts.length >= 20}
                      />
                    </label>
                    {requestedReceipts.length === 0 ? (
                      <p className="empty">No additional receipt staged yet.</p>
                    ) : (
                      <div className="receiptItems supplementItems">
                        {requestedReceipts.map((item, index) => (
                          <article className="receiptEditor" key={item.receipt.id}>
                            <div className="preview small">
                              {item.receipt.content_type === "application/pdf" ? (
                                <object data={item.preview} type="application/pdf">PDF receipt selected</object>
                              ) : (
                                <Image src={item.preview} alt={`Additional receipt ${index + 1} preview`} width={350} height={180} unoptimized />
                              )}
                            </div>
                            <div className="receiptMeta">
                              <div className="lineHeading">
                                <strong>Additional receipt {index + 1}</strong>
                                <button
                                  className="secondary"
                                  type="button"
                                  onClick={() => {
                                    URL.revokeObjectURL(item.preview);
                                    setSupplementItems((current) => ({
                                      ...current,
                                      [expense.id]: (current[expense.id] ?? []).filter((candidate) => candidate.receipt.id !== item.receipt.id),
                                    }));
                                  }}
                                >
                                  Remove
                                </button>
                              </div>
                              <small>{item.receipt.filename} · scan clean · encrypted storage</small>
                              <label>Merchant
                                <input
                                  required
                                  value={item.merchant}
                                  onChange={(event) => setSupplementItems((current) => ({
                                    ...current,
                                    [expense.id]: (current[expense.id] ?? []).map((candidate) => candidate.receipt.id === item.receipt.id ? { ...candidate, merchant: event.target.value } : candidate),
                                  }))}
                                />
                              </label>
                              <label>Amount (INR)
                                <input
                                  required
                                  min="0.01"
                                  step="0.01"
                                  type="number"
                                  value={item.amount}
                                  onChange={(event) => setSupplementItems((current) => ({
                                    ...current,
                                    [expense.id]: (current[expense.id] ?? []).map((candidate) => candidate.receipt.id === item.receipt.id ? { ...candidate, amount: event.target.value } : candidate),
                                  }))}
                                />
                              </label>
                              <label>Incurred date
                                <input
                                  required
                                  type="date"
                                  value={item.date}
                                  onChange={(event) => setSupplementItems((current) => ({
                                    ...current,
                                    [expense.id]: (current[expense.id] ?? []).map((candidate) => candidate.receipt.id === item.receipt.id ? { ...candidate, date: event.target.value } : candidate),
                                  }))}
                                />
                              </label>
                            </div>
                          </article>
                        ))}
                      </div>
                    )}
                  </>
                )}
                <div className="actions">
                  <button
                    disabled={busy || (receiptWasRequested && requestedReceipts.length === 0)}
                    onClick={() => void resubmit(expense)}
                  >
                    Submit requested information
                  </button>
                </div>
              </article>
            );
          })}
        </div>
      </section>
    )}
    <section className="panel"><div className="panelTitle"><div><p className="eyebrow">{role === "Reviewer" ? "REVIEW QUEUE" : "CLAIMS"}</p><h2>{role === "Reviewer" ? "Decisions that need you" : "Expense activity"}</h2></div><button className="secondary" onClick={() => void refresh()}>Refresh</button></div><div className="cards">{expenses.length === 0 && <p className="empty">No claims visible for this identity.</p>}{expenses.map((expense) => <article className="claim" key={expense.id}><div className="claimHead"><div><strong>{expense.merchant}</strong><small>{expense.category} · {expense.incurred_date}</small></div><strong>{formatMoney(expense.amount_minor, expense.currency)}</strong></div><div className="badges"><span className={`state ${expense.state.toLowerCase()}`}>{expense.state.replaceAll("_", " ")}</span>{expense.recommendation && <span className="recommendation">Recommendation—not decision: {expense.recommendation.replaceAll("_", " ")}</span>}</div><p>{expense.purpose}</p>{expense.receipt_items.length > 0 && <div className="receiptList"><strong>{expense.receipt_items.length} current receipt line{expense.receipt_items.length === 1 ? "" : "s"}</strong>{expense.receipt_items.map((item) => <button className="secondary" type="button" key={item.version_id} onClick={async () => { const blob = await download(`/api/v1/receipts/${item.receipt_id}/content`, identity); window.open(URL.createObjectURL(blob)); }}>Line {item.position} · {item.merchant} · {formatMoney(item.amount_minor, item.currency)} · {item.incurred_date}</button>)}</div>}{expense.receipt_history.length > 0 && <details className="checks"><summary>Receipt audit history · {expense.receipt_history.length} evidence version{expense.receipt_history.length === 1 ? "" : "s"}</summary>{expense.receipt_history.map((item) => <div className="checkRow" key={item.version_id}><span className={item.scan_status === "CLEAN" ? "pass" : "unknown"}>R{item.revision}</span><p><strong>Line {item.position} · {item.attachment_type.replaceAll("_", " ")}{item.is_current ? " · current" : " · superseded"}</strong><br />{item.filename} · {item.claimed_amount_minor ? formatMoney(item.claimed_amount_minor, item.claimed_currency || "INR") : "unconfirmed amount"} · {item.scan_status.toLowerCase()} · hash {item.content_hash.slice(0, 12)}…</p></div>)}</details>}{expense.information_request_message && <div className="infoRequest"><strong>Finance requested: {expense.requested_fields.join(", ")}</strong><p>{expense.information_request_message}</p></div>}{expense.checks.length > 0 && <div className="checks"><strong>{expense.checks.length} evidence checks</strong>{expense.checks.map((check) => <div className="checkRow" key={check.check_key}><span className={check.status.toLowerCase()}>{check.status}</span><p><strong>{check.source} · {check.reason_code.replaceAll("_", " ")}</strong><br />{check.explanation}</p></div>)}</div>}{expense.policy_citations.map((citation) => <blockquote key={citation.id}><strong>{citation.title}</strong><span>{citation.text}</span></blockquote>)}{(role === "Reviewer" || role === "Admin") && expense.state === "AWAITING_REVIEW" && <div className="actions"><button disabled={busy} onClick={() => void decide(expense, "APPROVE")}>Approve</button><button className="danger" disabled={busy} onClick={() => void decide(expense, "REJECT")}>Reject</button><button className="secondary" disabled={busy} onClick={() => void decide(expense, "REQUEST_INFORMATION")}>Request info</button></div>}{role === "Employee" && expense.state === "INFORMATION_REQUESTED" && <div className="actions"><button disabled={busy} onClick={() => void resubmit(expense)}>Update and resubmit</button></div>}{(role === "Reviewer" || role === "Admin") && (expense.state === "READY_TO_EXPORT" || expense.state === "EXPORT_FAILED") && <div className="handoff"><strong>Human-confirmed accounting handoff</strong><p>Confirm coding, then download an accountant-ready CSV. This does not move money.</p><button disabled={busy} onClick={() => void exportCsv(expense)}>Confirm coding & export CSV</button></div>}{expense.export?.status === "EXPORTED" && <div className="verified">✓ Exported to accountant-ready CSV</div>}</article>)}</div></section>
    {metrics && <section className="panel"><div className="panelTitle"><div><p className="eyebrow">OPERATING SIGNALS</p><h2>What the system can prove</h2></div><span className="step">Not payment evidence</span></div><div className="metricGrid">{Object.entries(metrics).filter(([key]) => key !== "note").map(([key, value]) => <div key={key}><strong>{value === null ? "—" : typeof value === "number" ? Math.round(value * 100) / 100 : value}</strong><span>{key.replaceAll("_", " ")}</span></div>)}</div><p className="empty">{String(metrics.note)}</p></section>}
    {audit && <section className="panel"><div className="panelTitle"><div><p className="eyebrow">AUDIT EVIDENCE</p><h2>Hash-linked event trail</h2></div><span className={audit.chain_valid ? "verified" : "invalid"}>{audit.chain_valid ? "✓ Chain verified" : "! Chain invalid"}</span></div><div className="timeline">{audit.events.map((event) => <div key={String(event.id)}><span>{String(event.sequence).padStart(2, "0")}</span><p><strong>{String(event.action)}</strong><small>{String(event.entity_type)} · {String(event.correlation_id).slice(0, 16)}…</small></p></div>)}</div></section>}
  </main>;
}
