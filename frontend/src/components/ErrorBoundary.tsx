import { AlertTriangle, RefreshCw } from "lucide-react";
import { Component, type ErrorInfo, type ReactNode } from "react";
import { translations, type Lang } from "../i18n/translations";

function currentLang(): Lang {
  const stored = localStorage.getItem("rp_lang");
  if (stored === "en" || stored === "zh") return stored;
  return typeof navigator !== "undefined" && navigator.language.startsWith("zh") ? "zh" : "en";
}

type Props = { children: ReactNode };
type State = { error: Error | null };

/**
 * Catches render-time errors anywhere below it so a single broken component
 * shows a friendly recovery screen instead of white-screening the whole app.
 * Self-contained (reads language directly) so it works even if the i18n
 * provider itself is the thing that threw.
 */
export class ErrorBoundary extends Component<Props, State> {
  state: State = { error: null };

  static getDerivedStateFromError(error: Error): State {
    return { error };
  }

  componentDidCatch(error: Error, info: ErrorInfo): void {
    // Surface to the console for debugging / error-tracking integrations.
    console.error("Unhandled UI error:", error, info.componentStack);
  }

  handleReload = (): void => {
    window.location.reload();
  };

  render(): ReactNode {
    const { error } = this.state;
    if (!error) return this.props.children;

    const t = translations[currentLang()];
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50 p-6">
        <div className="max-w-md w-full bg-white border border-slate-200 rounded-xl shadow-sm p-8 text-center space-y-4">
          <div className="mx-auto w-12 h-12 rounded-full bg-red-50 text-red-600 flex items-center justify-center">
            <AlertTriangle className="w-6 h-6" />
          </div>
          <h1 className="text-lg font-semibold text-slate-900">{t.errorTitle}</h1>
          <p className="text-sm text-slate-600">{t.errorBody}</p>
          {error.message && (
            <details className="text-left">
              <summary className="text-xs text-slate-500 cursor-pointer">{t.errorDetails}</summary>
              <pre className="mt-2 text-xs text-slate-500 bg-slate-50 rounded p-3 overflow-auto max-h-32 whitespace-pre-wrap">
                {error.message}
              </pre>
            </details>
          )}
          <button
            onClick={this.handleReload}
            className="inline-flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-lg text-sm font-medium hover:bg-indigo-700"
          >
            <RefreshCw className="w-4 h-4" />
            {t.errorReload}
          </button>
        </div>
      </div>
    );
  }
}
