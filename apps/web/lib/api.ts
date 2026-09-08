export type Expense = {
  id: string;
  merchant: string;
  amount_minor: number;
  currency: string;
  incurred_date: string;
  category: string;
  purpose: string;
  state: string;
  row_version: number;
  revision: number;
  receipt_present: boolean;
  recommendation: string | null;
  checks: Array<{ check_key: string; status: string; explanation: string; source: string }>;
};

export const identities = {
  Employee: "employee@acme.test",
  Reviewer: "reviewer@acme.test",
  Admin: "admin@acme.test",
  Auditor: "auditor@acme.test",
} as const;

export async function api<T>(path: string, identity: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`/api/v1${path}`, {
    ...init,
    headers: { "Content-Type": "application/json", "X-Demo-User": identity, ...init?.headers },
  });
  if (!response.ok) {
    const body = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(body.detail ?? body.title ?? "Request failed");
  }
  return response.json() as Promise<T>;
}

export function formatMoney(minor: number, currency: string): string {
  return new Intl.NumberFormat("en-IN", { style: "currency", currency }).format(minor / 100);
}
