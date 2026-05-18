import { test, expect } from "@playwright/test";

const FAKE_SVG =
  '<svg xmlns="http://www.w3.org/2000/svg"><text>Inner Diameter: 100</text></svg>';

const FAKE_BYTES = Buffer.from("FAKE_BINARY_CONTENT");

async function fillValidFormAndPreview(page: import("@playwright/test").Page) {
  await page.route("**/api/flange/preview", (route) => {
    route.fulfill({
      status: 200,
      contentType: "image/svg+xml",
      body: FAKE_SVG,
    });
  });

  await page.goto("/");

  await page.fill('[data-testid="field-inner_diameter_mm"]', "100");
  await page.fill('[data-testid="field-pcd_mm"]', "150");
  await page.fill('[data-testid="field-outer_diameter_mm"]', "200");
  await page.fill('[data-testid="field-bolt_hole_count"]', "4");
  await page.fill('[data-testid="field-bolt_hole_diameter_mm"]', "10");
  await page.fill('[data-testid="field-thickness_mm"]', "12");

  await page.getByTestId("submit").click();
  await expect(page.getByTestId("preview-svg")).toBeVisible();
}

test.describe("US2 — DWG/PDF Download", () => {
  test("download DWG button becomes enabled after preview and triggers download", async ({
    page,
  }) => {
    await fillValidFormAndPreview(page);

    await page.route("**/api/flange/dwg", (route) => {
      route.fulfill({
        status: 200,
        contentType: "application/acad",
        headers: {
          "Content-Disposition": 'attachment; filename="flange_test.dwg"',
        },
        body: FAKE_BYTES,
      });
    });

    const dwgBtn = page.getByTestId("download-dwg");
    await expect(dwgBtn).toBeEnabled();

    const [download] = await Promise.all([
      page.waitForEvent("download"),
      dwgBtn.click(),
    ]);

    expect(download).toBeTruthy();
    expect(download.suggestedFilename()).toMatch(/\.dwg$/i);
  });

  test("download PDF button becomes enabled after preview and triggers download", async ({
    page,
  }) => {
    await fillValidFormAndPreview(page);

    await page.route("**/api/flange/pdf", (route) => {
      route.fulfill({
        status: 200,
        contentType: "application/pdf",
        headers: {
          "Content-Disposition": 'attachment; filename="flange_test.pdf"',
        },
        body: FAKE_BYTES,
      });
    });

    const pdfBtn = page.getByTestId("download-pdf");
    await expect(pdfBtn).toBeEnabled();

    const [download] = await Promise.all([
      page.waitForEvent("download"),
      pdfBtn.click(),
    ]);

    expect(download).toBeTruthy();
    expect(download.suggestedFilename()).toMatch(/\.pdf$/i);
  });

  test("download buttons are disabled before preview", async ({ page }) => {
    await page.goto("/");

    await expect(page.getByTestId("download-dwg")).toBeDisabled();
    await expect(page.getByTestId("download-pdf")).toBeDisabled();
  });
});
