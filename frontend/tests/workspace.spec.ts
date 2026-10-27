import { test, expect } from "@playwright/test";
import { formatEvidence } from "../src/lib/attendance-contract";
import {
  eligibleWorkspace,
  applicationAccessActivated,
} from "../src/lib/auth-policy";
test("all requested screens render without errors or live requests", async ({
  page,
}) => {
  const errors: string[] = [];
  const live: string[] = [];
  page.on("pageerror", (e) => errors.push(e.message));
  page.on("request", (r) => {
    if (r.url().includes("supabase.co")) live.push(r.url());
  });
  for (const path of [
    "/",
    "/children",
    "/caregivers",
    "/relationships",
    "/questionnaires",
    "/attendance",
    "/attendance/pending",
    "/adl",
    "/support",
    "/data-quality",
    "/login",
  ]) {
    await page.goto(path);
    await expect(page.locator("h1")).toBeVisible();
    await expect(
      page.getByText("All people, records and dates below are synthetic."),
    ).toBeVisible();
  }
  expect(errors).toEqual([]);
  expect(live).toEqual([]);
});
test("directory search, filters, sorting and pagination", async ({ page }) => {
  await page.goto("/children");
  await expect(page.getByText("Showing 1–8 of 28 records")).toBeVisible();
  await page.getByRole("button", { name: "Next page" }).click();
  await expect(page.getByText("Page 2 of 4")).toBeVisible();
  await page
    .getByRole("textbox", { name: "Search records" })
    .fill("Demo child 02");
  await expect(page.locator("tbody tr")).toHaveCount(1);
  await page.getByRole("button", { name: "Clear search" }).click();
  await page
    .getByRole("combobox", { name: "Filter programme" })
    .selectOption("Demo programme A");
  await expect(page.getByText("Showing 1–8 of 14 records")).toBeVisible();
  await page.getByRole("button", { name: "Name / record" }).click();
  await expect(page.locator("th").first()).toHaveAttribute(
    "aria-sort",
    "descending",
  );
});
test("forms open explicitly; demo child add and edit", async ({ page }) => {
  await page.goto("/children");
  await expect(page.getByRole("dialog")).toHaveCount(0);
  await page.getByRole("button", { name: "Add child", exact: true }).click();
  const dialog = page.getByRole("dialog");
  await dialog.getByLabel("Display name").fill("Demo added child");
  await dialog.getByRole("button", { name: "Save demo record" }).click();
  await page
    .getByRole("textbox", { name: "Search records" })
    .fill("Demo added child");
  await expect(page.locator("tbody tr")).toHaveCount(1);
  await page.getByRole("button", { name: "Edit Demo added child" }).click();
  await page.getByLabel("Display name").fill("Demo changed child");
  await page.getByRole("button", { name: "Save demo record" }).click();
  await page
    .getByRole("textbox", { name: "Search records" })
    .fill("Demo changed child");
  await expect(page.locator("tbody tr")).toHaveCount(1);
});
test("pending evidence stays unverified; review notes cannot approve", async ({
  page,
}) => {
  await page.goto("/attendance/pending");
  await expect(
    page.getByText("Unverified source evidence.", { exact: false }),
  ).toBeVisible();
  await expect(page.locator("tbody .badge.success")).toHaveCount(0);
  await page.locator("tbody .row-action").first().click();
  const dialog = page.getByRole("dialog");
  await expect(dialog.getByText("Immutable source reference")).toBeVisible();
  await expect(
    dialog.getByRole("button", { name: "Approve identity — unavailable" }),
  ).toBeDisabled();
  await dialog
    .getByLabel("Review note")
    .fill("Demo note: obtain exact ID crosswalk");
  await dialog.getByRole("button", { name: "Save demo note" }).click();
  await page.locator("tbody .row-action").first().click();
  await expect(page.getByLabel("Review note")).toHaveValue(
    "Demo note: obtain exact ID crosswalk",
  );
});
test("verified attendance filters only accepted demo events", async ({
  page,
}) => {
  await page.goto("/attendance");
  await expect(page.locator("tbody .badge.success")).toHaveCount(8);
  await page.getByLabel("Attendance from date").fill("2025-08-25");
  await page.getByLabel("Attendance to date").fill("2025-08-27");
  await expect(page.locator("tbody tr")).toHaveCount(3);
});
test("collapsed and mobile navigation retain visible accessible icons", async ({
  page,
}) => {
  await page.goto("/");
  await page.getByRole("button", { name: "Collapse navigation" }).click();
  await expect(
    page.getByRole("link", { name: "Children", exact: true }).locator("svg"),
  ).toBeVisible();
  await page.getByRole("link", { name: "Children", exact: true }).click();
  await expect(page.locator("h1")).toHaveText("Children");
  await page.setViewportSize({ width: 390, height: 844 });
  await page.getByRole("button", { name: "Open navigation" }).click();
  await page.getByRole("link", { name: "Caregivers", exact: true }).click();
  await expect(page.locator("h1")).toHaveText("Caregivers");
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= innerWidth,
    ),
  ).toBe(true);
});
test("OAuth and live API are fail-closed; host guard rejects nonlocal access", async ({
  request,
}) => {
  expect((await request.post("/auth/sign-in")).status()).toBe(503);
  expect((await request.get("/auth/callback?code=demo")).status()).toBe(503);
  expect((await request.get("/api/live")).status()).toBe(503);
  expect(
    (
      await request.get("/", { headers: { host: "unapproved.example" } })
    ).status(),
  ).toBe(403);
});
test("trusted Workspace eligibility never grants application access", () => {
  const user = {
    id: "demo",
    email: "demo@goalkeep.net",
    email_confirmed_at: "DEMO",
    app_metadata: { provider: "google" },
    identities: [
      {
        provider: "google",
        identity_data: {
          email: "demo@goalkeep.net",
          email_verified: true,
          hd: "goalkeep.net",
        },
      },
    ],
  };
  const claims = {
    sub: "demo",
    session_id: "demo-session",
    amr: [{ method: "oauth" }],
  };
  expect(eligibleWorkspace(user, claims)).toBe(true);
  expect(applicationAccessActivated).toBe(false);
  expect(
    eligibleWorkspace({ ...user, app_metadata: { provider: "email" } }, claims),
  ).toBe(false);
  expect(
    eligibleWorkspace(
      {
        ...user,
        identities: [
          {
            provider: "google",
            identity_data: {
              email: "demo@goalkeep.net",
              email_verified: false,
              hd: "goalkeep.net",
            },
          },
        ],
      },
      claims,
    ),
  ).toBe(false);
  expect(eligibleWorkspace({ ...user, identities: [] }, claims)).toBe(false);
  expect(
    eligibleWorkspace(user, { ...claims, amr: [{ method: "password" }] }),
  ).toBe(false);
});
test("capture synthetic preview screens", async ({ page }) => {
  await page.goto("/");
  await page.screenshot({
    path: "../docs/previews/dashboard.png",
    fullPage: true,
  });
  await page.goto("/attendance/pending");
  await page.screenshot({
    path: "../docs/previews/pending-attendance.png",
    fullPage: true,
  });
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/children");
  await page.screenshot({
    path: "../docs/previews/mobile-children.png",
    fullPage: true,
  });
});

test("evidence formatting preserves zero, false and opaque source values", () => {
  expect(formatEvidence(0)).toBe("0");
  expect(formatEvidence(false)).toBe("false");
  expect(formatEvidence(null)).toBe("Not recorded");
  expect(formatEvidence("P")).toBe("P");
  expect(formatEvidence({ source: "opaque" })).toBe('{\"source\":\"opaque\"}');
});
