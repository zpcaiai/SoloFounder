// Complementary to src/components/ErrorBoundary.test.tsx (which checks the
// recovery title + reload button). This file checks pass-through and that the
// underlying error message is surfaced for debugging.
import React from "react";
import { render, screen } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { ErrorBoundary } from "../components/ErrorBoundary";

function Boom(): never {
  throw new Error("kaboom-detail");
}

describe("ErrorBoundary behavior", () => {
  beforeEach(() => localStorage.clear());
  afterEach(() => vi.restoreAllMocks());

  it("renders children unchanged when nothing throws", () => {
    render(
      <ErrorBoundary>
        <div>healthy child</div>
      </ErrorBoundary>,
    );
    expect(screen.getByText("healthy child")).toBeInTheDocument();
  });

  it("surfaces the underlying error message in the fallback", () => {
    vi.spyOn(console, "error").mockImplementation(() => undefined);
    render(
      <ErrorBoundary>
        <Boom />
      </ErrorBoundary>,
    );
    expect(screen.getByText(/kaboom-detail/)).toBeInTheDocument();
  });
});
