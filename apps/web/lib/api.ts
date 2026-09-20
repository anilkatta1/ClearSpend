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
  receipt_id: string | null;
  receipt: ReceiptUpload | null;
  receipt_history: Array<{ version_id: string; receipt_id: string; revision: number; attachment_type: string; is_current: boolean; supersedes_id: string | null; content_hash: string; filename: string; scan_status: string; security_flags: string[]; created_at: string }>;
  information_request_message: string | null;
  requested_fields: string[];
  policy_citations: Array<{ id: string; title: string; text: string }>;
  export: { id: string; status: string; account_code: string; cost_center: string; error_code: string | null; error_detail: string | null } | null;
  recommendation: string | null;
  checks: Array<{ check_key: string; status: string; reason_code: string; explanation: string; source: string; policy_section_ids: string[] }>;
};

export type ReceiptUpload = {
  id: string;
  filename: string;
  content_type: string;
  extraction_status: string;
  scan_status: string;
  scan_result: string | null;
  security_flags: string[];
  extracted_merchant: string | null;
  extracted_date: string | null;
  extracted_amount_minor: number | null;
  extracted_currency: string | null;
  preview_url?: string;
};

export const identities = {
  Employee: "employee@acme.test",
  Reviewer: "reviewer@acme.test",
  Admin: "admin@acme.test",
  Auditor: "auditor@acme.test",
} as const;

export async function api<T>(path: string, identity: string, init?: RequestInit): Promise<T> {
  const multipart = init?.body instanceof FormData;
  const response = await fetch(`/api/v1${path}`, {
    ...init,
    headers: { ...(multipart ? {} : { "Content-Type": "application/json" }), "X-Demo-User": identity, ...init?.headers },
  });
  if (!response.ok) {
    const body = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(body.detail ?? body.title ?? "Request failed");
  }
  return response.json() as Promise<T>;
}

export async function download(path: string, identity: string): Promise<Blob> {
  const response = await fetch(path, { headers: { "X-Demo-User": identity } });
  if (!response.ok) throw new Error("Download failed");
  return response.blob();
}

export function formatMoney(minor: number, currency: string): string {
  return new Intl.NumberFormat("en-IN", { style: "currency", currency }).format(minor / 100);
}
