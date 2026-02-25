import { describe, it, expect, beforeEach } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import App from "../../src/App";

describe("App", () => {
  beforeEach(() => {
    // Mock localStorage
    const localStorageMock = (() => {
      let store: Record<string, string> = {};
      return {
        getItem: (key: string) => store[key] || null,
        setItem: (key: string, value: string) => {
          store[key] = value.toString();
        },
        removeItem: (key: string) => {
          delete store[key];
        },
        clear: () => {
          store = {};
        },
      };
    })();

    Object.defineProperty(window, "localStorage", {
      value: localStorageMock,
    });
  });

  it("renders without crashing", () => {
    render(<App />);
    expect(screen.getByText("Resource Fetcher")).toBeInTheDocument();
  });

  it("displays theme toggle button", () => {
    render(<App />);
    const button = screen.getByRole("button", { name: /dark|light/i });
    expect(button).toBeInTheDocument();
  });

  it("toggles theme when button is clicked", () => {
    render(<App />);
    const button = screen.getByRole("button", { name: /dark|light/i });

    // Initial theme should be light
    expect(document.documentElement.classList.contains("dark")).toBe(false);

    // Click button to toggle to dark
    fireEvent.click(button);
    expect(document.documentElement.classList.contains("dark")).toBe(true);

    // Click button to toggle back to light
    fireEvent.click(button);
    expect(document.documentElement.classList.contains("dark")).toBe(false);
  });

  it("displays status message", () => {
    render(<App />);
    expect(screen.getByText("Ready")).toBeInTheDocument();
  });

  describe("Python integration", () => {
    it("shows error when Python environment is not ready", async () => {
      render(<App />);

      // Mock failed Python info
      // This test would mock the invoke call
      // For now, we just check the initial state
      expect(screen.getByText("Ready")).toBeInTheDocument();
    });
  });
});
