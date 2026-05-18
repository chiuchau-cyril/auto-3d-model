import { test, expect } from "@playwright/test";

const FAKE_SVG =
  '<svg xmlns="http://www.w3.org/2000/svg"><text>Inner Diameter: 100</text></svg>';

async function fillValidForm(page: import("@playwright/test").Page) {
  await page.fill('[data-testid="field-inner_diameter_mm"]', "100");
  await page.fill('[data-testid="field-pcd_mm"]', "150");
  await page.fill('[data-testid="field-outer_diameter_mm"]', "200");
  await page.fill('[data-testid="field-bolt_hole_count"]', "4");
  await page.fill('[data-testid="field-bolt_hole_diameter_mm"]', "10");
  await page.fill('[data-testid="field-thickness_mm"]', "12");
}

test.describe("US1 — SVG Preview", () => {
  test("displays SVG preview after submitting valid form", async ({ page }) => {
    await page.route("**/api/flange/preview", (route) => {
      route.fulfill({
        status: 200,
        contentType: "image/svg+xml",
        body: FAKE_SVG,
      });
    });

    await page.goto("/");
    await fillValidForm(page);

    const submit = page.getByTestId("submit");
    await expect(submit).toBeEnabled();
    await submit.click();

    const preview = page.getByTestId("preview-svg");
    await expect(preview).toBeVisible();
    await expect(preview).toContainText("Inner Diameter");
  });

  test("submit button stays disabled when PCD is less than inner diameter", async ({
    page,
  }) => {
    await page.goto("/");

    // Fill all fields but with PCD < inner diameter
    await page.fill('[data-testid="field-inner_diameter_mm"]', "150");
    await page.fill('[data-testid="field-pcd_mm"]', "100");
    await page.fill('[data-testid="field-outer_diameter_mm"]', "200");
    await page.fill('[data-testid="field-bolt_hole_count"]', "4");
    await page.fill('[data-testid="field-bolt_hole_diameter_mm"]', "10");
    await page.fill('[data-testid="field-thickness_mm"]', "12");

    const submit = page.getByTestId("submit");
    await expect(submit).toBeDisabled();

    // Error message should appear for pcd_mm
    await expect(page.getByTestId("error-pcd_mm")).toBeVisible();
    await expect(page.getByTestId("error-pcd_mm")).toContainText("PCD 必須大於內徑");
  });
});
