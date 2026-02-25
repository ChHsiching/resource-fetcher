import { test, expect } from "@playwright/test";

test.describe("Resource Fetcher GUI E2E Tests", () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the app
    await page.goto("http://localhost:1420");
  });

  test("should display main application", async ({ page }) => {
    // Check main heading
    await expect(page.getByText("Resource Fetcher")).toBeVisible();

    // Check URL input section
    await expect(page.getByText("Download URL")).toBeVisible();
    await expect(page.getByPlaceholder("Enter album or song URL...")).toBeVisible();

    // Check configuration section
    await expect(page.getByText("Configuration")).toBeVisible();
  });

  test("should toggle theme between light and dark", async ({ page }) => {
    // Find theme toggle button
    const themeButton = page.getByRole("button").filter({ hasText: /dark|light/i });

    // Initial theme should be light
    await expect(page.locator("html")).not.toHaveClass(/dark/);

    // Click to toggle to dark
    await themeButton.click();
    await expect(page.locator("html")).toHaveClass(/dark/);

    // Click to toggle back to light
    await themeButton.click();
    await expect(page.locator("html")).not.toHaveClass(/dark/);
  });

  test("should validate URL input", async ({ page }) => {
    const urlInput = page.getByPlaceholder("Enter album or song URL...");
    const downloadAlbumBtn = page.getByRole("button", { name: /Download Album/i });
    const downloadSongBtn = page.getByRole("button", { name: /Download Song/i });

    // Buttons should be disabled with empty input
    await expect(downloadAlbumBtn).toBeDisabled();
    await expect(downloadSongBtn).toBeDisabled();

    // Buttons should be disabled with invalid URL
    await urlInput.fill("not-a-valid-url");
    await expect(downloadAlbumBtn).toBeDisabled();
    await expect(downloadSongBtn).toBeDisabled();

    // Buttons should be enabled with valid URL
    await urlInput.fill("https://example.com/album");
    await expect(downloadAlbumBtn).toBeEnabled();
    await expect(downloadSongBtn).toBeEnabled();
  });

  test("should expand and collapse advanced settings", async ({ page }) => {
    const advancedButton = page.getByRole("button", { name: /Advanced Settings/i });

    // Advanced settings should be collapsed initially
    await expect(page.getByText("Timeout (seconds)")).not.toBeVisible();

    // Click to expand
    await advancedButton.click();
    await expect(page.getByText("Timeout (seconds)")).toBeVisible();
    await expect(page.getByText("Retries")).toBeVisible();

    // Click to collapse
    await advancedButton.click();
    await expect(page.getByText("Timeout (seconds)")).not.toBeVisible();
  });

  test("should update configuration values", async ({ page }) => {
    // Output directory
    const outputDirInput = page.getByPlaceholder("Downloads");
    await outputDirInput.fill("/custom/path");
    await expect(outputDirInput).toHaveValue("/custom/path");

    // Download limit
    const limitInput = page.getByPlaceholder("Leave empty to download all songs");
    await limitInput.fill("10");
    await expect(limitInput).toHaveValue("10");
  });

  test("should toggle checkboxes", async ({ page }) => {
    const advancedButton = page.getByRole("button", { name: /Advanced Settings/i });
    await advancedButton.click();

    // Overwrite checkbox
    const overwriteCheckbox = page.getByRole("checkbox", { name: /Overwrite existing files/i });
    await overwriteCheckbox.check();
    await expect(overwriteCheckbox).toBeChecked();

    await overwriteCheckbox.uncheck();
    await expect(overwriteCheckbox).not.toBeChecked();

    // Verbose checkbox
    const verboseCheckbox = page.getByRole("checkbox", { name: /Verbose output/i });
    await verboseCheckbox.check();
    await expect(verboseCheckbox).toBeChecked();
  });

  test("should display status message", async ({ page }) => {
    const statusElement = page.getByText("Ready");
    await expect(statusElement).toBeVisible();
  });

  test("should handle URL paste action", async ({ page }) => {
    const urlInput = page.getByPlaceholder("Enter album or song URL...");

    // Simulate paste
    await urlInput.fill("https://example.com/test");
    await expect(urlInput).toHaveValue("https://example.com/test");
  });
});
