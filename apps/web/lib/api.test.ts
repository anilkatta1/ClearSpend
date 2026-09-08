import { describe, expect, it } from "vitest";
import { formatMoney } from "./api";

describe("formatMoney", () => {
  it("formats integer minor units without losing paise", () => {
    expect(formatMoney(12345, "INR")).toContain("123.45");
  });
});
