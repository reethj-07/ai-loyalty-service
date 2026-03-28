import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { ArrowRight, ShieldCheck, Sparkles, LineChart, LockKeyhole } from "lucide-react";
import { useAuth } from "@/contexts/AuthContext";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

export default function Login() {
  const navigate = useNavigate();
  const { login, signup, requestPasswordReset, isAuthenticated } = useAuth();
  const [mode, setMode] = useState<"signin" | "signup">("signin");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [resetEmail, setResetEmail] = useState("");
  const [showForgotPassword, setShowForgotPassword] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const signupPasswordErrors = [
    password.length >= 8 ? null : "At least 8 characters",
    /[A-Z]/.test(password) ? null : "One uppercase letter",
    /[a-z]/.test(password) ? null : "One lowercase letter",
    /\d/.test(password) ? null : "One number",
  ].filter(Boolean) as string[];

  // Redirect if already authenticated
  useEffect(() => {
    if (isAuthenticated) {
      navigate("/dashboard");
    }
  }, [isAuthenticated, navigate]);

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setError(null);
    setSuccess(null);

    if (mode === "signup" && password !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    if (mode === "signup" && signupPasswordErrors.length > 0) {
      setError(`Password requirements not met: ${signupPasswordErrors.join(", ")}`);
      return;
    }

    setIsLoading(true);

    try {
      if (mode === "signup") {
        await signup(email, password);
        const createdSessionToken = localStorage.getItem("auth_token");

        if (createdSessionToken) {
          navigate("/dashboard");
          return;
        }

        setSuccess("Account created successfully. Please verify your email if required, then sign in.");
        setMode("signin");
        setPassword("");
        setConfirmPassword("");
        return;
      } else {
        await login(email, password);
        navigate("/dashboard");
      }
    } catch (err: any) {
      const message =
        err?.message ||
        (mode === "signup"
          ? "Sign up failed. Please verify your details and try again."
          : "Sign in failed. Please verify your credentials.");
      setError(message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleForgotPassword = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setError(null);
    setSuccess(null);
    setIsLoading(true);

    try {
      const message = await requestPasswordReset(resetEmail || email);
      setSuccess(message);
      setShowForgotPassword(false);
    } catch (err: any) {
      setError(err?.message || "Unable to process password reset request.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background grid lg:grid-cols-2">
      <div className="hidden lg:flex relative overflow-hidden border-r border-border/60">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_top,_hsl(var(--primary)/0.28),transparent_55%),radial-gradient(circle_at_80%_80%,_hsl(var(--accent)/0.15),transparent_45%)]" />
        <div className="relative z-10 w-full p-14 flex flex-col justify-between">
          <div className="inline-flex items-center gap-3 rounded-full border border-border/60 bg-card/70 px-4 py-2 backdrop-blur-sm w-fit">
            <div className="h-7 w-7 rounded-md bg-primary/20 text-primary flex items-center justify-center">
              <Sparkles className="h-4 w-4" />
            </div>
            <span className="text-sm text-muted-foreground">Asteria Growth Cloud</span>
          </div>

          <div>
            <h1 className="text-4xl font-semibold leading-tight tracking-tight text-foreground">
              Premium Growth Operating System for Customer Revenue Teams
            </h1>
            <p className="mt-4 text-base text-muted-foreground max-w-xl">
              Orchestrate retention, AI campaigns, and lifecycle analytics from one secure control center.
            </p>

            <div className="mt-8 space-y-4">
              <div className="flex items-center gap-3 text-sm text-muted-foreground">
                <ShieldCheck className="h-4 w-4 text-primary" />
                Enterprise-grade auth with Supabase and role-based access
              </div>
              <div className="flex items-center gap-3 text-sm text-muted-foreground">
                <LineChart className="h-4 w-4 text-primary" />
                Unified campaigns, member intelligence, and KPI visibility
              </div>
              <div className="flex items-center gap-3 text-sm text-muted-foreground">
                <LockKeyhole className="h-4 w-4 text-primary" />
                Production-ready API integration with protected operations
              </div>
            </div>
          </div>

          <div className="text-xs text-muted-foreground">© {new Date().getFullYear()} Asteria Cloud</div>
        </div>
      </div>

      <div className="flex items-center justify-center p-6 lg:p-10">
        <div className="w-full max-w-md rounded-2xl border border-border/70 bg-card/90 p-8 shadow-2xl backdrop-blur-sm">
          <div className="mb-8">
            <div className="mb-5 flex items-center gap-3">
              <div className="w-10 h-10 bg-primary rounded-lg flex items-center justify-center shadow-lg">
                <span className="text-primary-foreground font-semibold text-lg">A</span>
              </div>
              <div>
                <div className="text-sm text-muted-foreground">
                  {mode === "signup" ? "Create account" : "Welcome back"}
                </div>
                <div className="font-semibold text-foreground">Asteria Growth Cloud</div>
              </div>
            </div>
            <h2 className="text-2xl font-semibold text-foreground">
              {mode === "signup" ? "Create your workspace account" : "Sign in to your workspace"}
            </h2>
            <p className="mt-2 text-sm text-muted-foreground">
              {mode === "signup"
                ? "First time here? Create your account to start using the dashboard."
                : "Already have an account? Sign in to continue."}
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <label className="text-sm font-medium text-foreground" htmlFor="email">Email</label>
              <Input
                id="email"
                type="email"
                autoComplete="email"
                placeholder="you@company.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="h-11"
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium text-foreground" htmlFor="password">Password</label>
              <Input
                id="password"
                type="password"
                autoComplete={mode === "signup" ? "new-password" : "current-password"}
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                className="h-11"
              />
            </div>

            {mode === "signup" && password.length > 0 && (
              <div className="rounded-lg border border-border/60 bg-muted/20 px-3 py-2 text-xs text-muted-foreground">
                Password must include at least 8 chars, uppercase, lowercase, and number.
              </div>
            )}

            {mode === "signup" && (
              <div className="space-y-2">
                <label className="text-sm font-medium text-foreground" htmlFor="confirmPassword">Confirm Password</label>
                <Input
                  id="confirmPassword"
                  type="password"
                  autoComplete="new-password"
                  placeholder="••••••••"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  required
                  className="h-11"
                />
              </div>
            )}

            {error && (
              <div className="rounded-lg border border-destructive/40 bg-destructive/10 px-3 py-2 text-sm text-destructive">
                {error}
              </div>
            )}

            {success && (
              <div className="rounded-lg border border-emerald-500/40 bg-emerald-500/10 px-3 py-2 text-sm text-emerald-300">
                {success}
              </div>
            )}

            <Button
              type="submit"
              className="w-full h-11 text-base"
              disabled={isLoading}
            >
              {isLoading ? (
                <>
                  <div className="mr-2 h-4 w-4 animate-spin rounded-full border-2 border-background border-t-transparent" />
                  {mode === "signup" ? "Creating account..." : "Signing in..."}
                </>
              ) : (
                <>
                  {mode === "signup" ? "Create account" : "Continue"}
                  <ArrowRight className="ml-2 w-4 h-4" />
                </>
              )}
            </Button>

            {mode === "signin" && (
              <button
                type="button"
                className="w-full text-sm text-primary hover:underline"
                onClick={() => {
                  setShowForgotPassword((prev) => !prev);
                  setError(null);
                  setSuccess(null);
                  setResetEmail(email);
                }}
              >
                Forgot password?
              </button>
            )}
          </form>

          {showForgotPassword && (
            <form onSubmit={handleForgotPassword} className="mt-4 space-y-3 rounded-lg border border-border/60 bg-muted/20 p-3">
              <label className="text-sm font-medium text-foreground" htmlFor="resetEmail">Reset email</label>
              <Input
                id="resetEmail"
                type="email"
                autoComplete="email"
                placeholder="you@company.com"
                value={resetEmail}
                onChange={(e) => setResetEmail(e.target.value)}
                required
                className="h-10"
              />
              <Button type="submit" className="w-full h-10" disabled={isLoading}>
                Send reset link
              </Button>
            </form>
          )}

          <div className="mt-6 text-sm text-muted-foreground">
            {mode === "signin" ? (
              <>
                Don&apos;t have an account?{" "}
                <button
                  type="button"
                  className="text-primary hover:underline"
                  onClick={() => {
                    setMode("signup");
                    setError(null);
                    setSuccess(null);
                  }}
                >
                  Sign up
                </button>
              </>
            ) : (
              <>
                Already have an account?{" "}
                <button
                  type="button"
                  className="text-primary hover:underline"
                  onClick={() => {
                    setMode("signin");
                    setError(null);
                    setSuccess(null);
                  }}
                >
                  Sign in
                </button>
              </>
            )}
          </div>

          <p className="mt-3 text-xs text-muted-foreground">
            Tip: if sign in fails right after sign up, confirm the user in Supabase Auth first.
          </p>
        </div>
      </div>
    </div>
  );
}
