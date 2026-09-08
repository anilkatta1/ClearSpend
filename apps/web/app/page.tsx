"use client";

import { FormEvent, useCallback, useEffect, useState } from "react";
import { api, Expense, formatMoney, identities } from "@/lib/api";

type RoleName = keyof typeof identities;

export default function Home() {
  const [role, setRole] = useState<RoleName>("Employee");
  const [expenses, setExpenses] = useState<Expense[]>([]);
  const [audit, setAudit] = useState<{ chain_valid: boolean; events: Array<Record<string, unknown>> } | null>(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const identity = identities[role];

  const refresh = useCallback(async () => {
    setError("");
    try {
      setExpenses(await api<Expense[]>("/expenses", identity));
      if (role === "Admin" || role === "Auditor") {
        setAudit(await api("/audit-events", identity));
      } else setAudit(null);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Unable to load data");
    }
  }, [identity, role]);

  useEffect(() => {
    // This effect intentionally synchronizes the dashboard with the selected demo identity.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    void refresh();
  }, [refresh]);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); setBusy(true); setError("");
    const form = event.currentTarget;
    const data = new FormData(form);
    try {
      await api("/expenses", identity, {
        method: "POST",
        headers: { "Idempotency-Key": crypto.randomUUID() },
        body: JSON.stringify({
          merchant: data.get("merchant"), amount_minor: Math.round(Number(data.get("amount")) * 100),
          currency: "INR", incurred_date: data.get("date"), category: data.get("category"),
          purpose: data.get("purpose"), receipt_present: data.get("receipt") === "on",
        }),
      });
      form.reset(); await refresh();
    } catch (cause) { setError(cause instanceof Error ? cause.message : "Submission failed"); }
    finally { setBusy(false); }
  }

  async function decide(expense: Expense, action: "APPROVE" | "REJECT" | "REQUEST_INFORMATION") {
    const reason = action === "APPROVE" && expense.recommendation === "APPROVE_RECOMMENDED" ? "" : window.prompt("Reason required for rejection, override, or information request:") ?? "";
    setBusy(true);
    try {
      await api(`/expenses/${expense.id}/decisions`, identity, { method: "POST", headers: { "Idempotency-Key": crypto.randomUUID() }, body: JSON.stringify({ action, reason, expected_row_version: expense.row_version }) });
      await refresh();
    } catch (cause) { setError(cause instanceof Error ? cause.message : "Decision failed"); }
    finally { setBusy(false); }
  }

  return (
    <main>
      <header className="topbar">
        <div className="brand"><span className="mark">C</span><div><strong>ClearSpend</strong><small>Evidence-first expense operations</small></div></div>
        <label className="role">View as<select value={role} onChange={(event) => setRole(event.target.value as RoleName)}>{Object.keys(identities).map((name) => <option key={name}>{name}</option>)}</select></label>
      </header>

      <section className="hero">
        <div><p className="eyebrow">FINANCE CONTROL CENTER</p><h1>Every expense decision,<br /><em>clear and accountable.</em></h1><p>Deterministic policy checks, bounded AI explanations, and human authority—joined by one audit trail.</p></div>
        <div className="trust"><span>● System operational</span><strong>{expenses.filter((e) => e.state === "AWAITING_REVIEW").length}</strong><small>awaiting review</small></div>
      </section>

      {error && <div className="alert" role="alert">{error}</div>}

      {role === "Employee" && <section className="panel"><div className="panelTitle"><div><p className="eyebrow">NEW CLAIM</p><h2>Submit reimbursement</h2></div><span className="step">Policy captured on submit</span></div><form onSubmit={submit} className="formGrid"><label>Merchant<input name="merchant" required placeholder="e.g. Taj Hotels" /></label><label>Amount (INR)<input name="amount" required min="0.01" step="0.01" type="number" /></label><label>Incurred date<input name="date" required type="date" /></label><label>Category<select name="category"><option>travel</option><option>meals</option><option>office</option><option>alcohol</option><option>personal</option></select></label><label className="wide">Business purpose<textarea name="purpose" required placeholder="Who, why, and expected business outcome" /></label><label className="check"><input name="receipt" type="checkbox" /> Receipt metadata verified</label><button disabled={busy} type="submit">{busy ? "Submitting…" : "Submit for assessment →"}</button></form></section>}

      <section className="panel"><div className="panelTitle"><div><p className="eyebrow">{role === "Reviewer" ? "REVIEW QUEUE" : "CLAIMS"}</p><h2>{role === "Reviewer" ? "Decisions that need you" : "Expense activity"}</h2></div><button className="secondary" onClick={() => void refresh()}>Refresh</button></div>
        <div className="cards">{expenses.length === 0 && <p className="empty">No claims visible for this identity.</p>}{expenses.map((expense) => <article className="claim" key={expense.id}><div className="claimHead"><div><strong>{expense.merchant}</strong><small>{expense.category} · {expense.incurred_date}</small></div><strong>{formatMoney(expense.amount_minor, expense.currency)}</strong></div><div className="badges"><span className={`state ${expense.state.toLowerCase()}`}>{expense.state.replaceAll("_", " ")}</span>{expense.recommendation && <span className="recommendation">{expense.recommendation.replaceAll("_", " ")}</span>}</div><p>{expense.purpose}</p>{expense.checks.length > 0 && <details><summary>{expense.checks.length} policy checks</summary>{expense.checks.map((check) => <div className="checkRow" key={check.check_key}><span className={check.status.toLowerCase()}>{check.status}</span><p><strong>{check.source}</strong> · {check.explanation}</p></div>)}</details>}{(role === "Reviewer" || role === "Admin") && expense.state === "AWAITING_REVIEW" && <div className="actions"><button disabled={busy} onClick={() => void decide(expense, "APPROVE")}>Approve</button><button className="danger" disabled={busy} onClick={() => void decide(expense, "REJECT")}>Reject</button><button className="secondary" disabled={busy} onClick={() => void decide(expense, "REQUEST_INFORMATION")}>Request info</button></div>}</article>)}</div>
      </section>

      {audit && <section className="panel"><div className="panelTitle"><div><p className="eyebrow">AUDIT EVIDENCE</p><h2>Hash-linked event trail</h2></div><span className={audit.chain_valid ? "verified" : "invalid"}>{audit.chain_valid ? "✓ Chain verified" : "! Chain invalid"}</span></div><div className="timeline">{audit.events.map((event) => <div key={String(event.id)}><span>{String(event.sequence).padStart(2, "0")}</span><p><strong>{String(event.action)}</strong><small>{String(event.entity_type)} · {String(event.correlation_id).slice(0, 16)}…</small></p></div>)}</div></section>}
    </main>
  );
}
