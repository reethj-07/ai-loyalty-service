import { useState, useEffect, useMemo } from "react";
import { Link, useNavigate } from "react-router-dom";
import { ArrowRight, ShieldCheck, Sparkles, LineChart, LockKeyhole, Eye, EyeOff } from "lucide-react";
import { useAuth } from "@/contexts/AuthContext";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

export default function Login() {
  const navigate = useNavigate();
  const { login, signup, requestPasswordReset, isAuthenticated } = useAuth();
  const [mode, setMode] = useState<"signin" | "signup">("signin");
  const [fullName, setFullName] = useState("");
  const [company, setCompany] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [resetEmail, setResetEmail] = useState("");
  const [showForgotPassword, setShowForgotPassword] = useState(false);
  const [acceptLegal, setAcceptLegal] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const signupPasswordErrors = [
    password.length >= 8 ? null : "At least 8 characters",
    /[A-Z]/.test(password) ? null : "One uppercase letter",
    /[a-z]/.test(password) ? null : "One lowercase letter",
    /\d/.test(password) ? null : "One number",
  ].filter(Boolean) as string[];

  const passwordStrength = useMemo(() => {
    if (!password) {
      return { score: 0, label: "", tone: "bg-muted" };
    }

    let score = 0;
    if (password.length >= 8) score += 1;
    if (/[A-Z]/.test(password) && /[a-z]/.test(password)) score += 1;
    if (/\d/.test(password)) score += 1;
    if (/[^A-Za-z0-9]/.test(password) || password.length >= 12) score += 1;

    if (score <= 1) return { score, label: "Weak", tone: "bg-red-500" };
    if (score === 2) return { score, label: "Fair", tone: "bg-amber-500" };
    if (score === 3) return { score, label: "Good", tone: "bg-yellow-500" };
    return { score, label: "Strong", tone: "bg-emerald-500" };
  }, [password]);

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

    const normalizedEmail = email.trim().toLowerCase();
    if (!normalizedEmail) {
      setError("Please enter your work email.");
      return;
    }

    if (mode === "signup" && password !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    if (mode === "signup" && signupPasswordErrors.length > 0) {
      setError(`Password requirements not met: ${signupPasswordErrors.join(", ")}`);
      return;
    }

    if (mode === "signup" && !acceptLegal) {
      setError("Please accept the Terms and Privacy Policy to create your account.");
      return;
    }

    setIsLoading(true);

    try {
      if (mode === "signup") {
        await signup(normalizedEmail, password, {
          full_name: fullName.trim() || undefined,
          company: company.trim() || undefined,
        });
        const createdSessionToken = localStorage.getItem("auth_token");

        if (createdSessionToken) {
          navigate("/dashboard");
          return;
        }

        setSuccess("Account created. Check your inbox to verify your email, then sign in.");
        setMode("signin");
        setFullName("");
        setCompany("");
        setAcceptLegal(false);
        setPassword("");
        setConfirmPassword("");
        return;
      } else {
        await login(normalizedEmail, password);
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
              Loyalty Experience Platform for Retention and Revenue Teams
            </h1>
            <p className="mt-4 text-base text-muted-foreground max-w-xl">
              Launch white-label loyalty programs, AI-driven lifecycle journeys, and real-time performance analytics from one secure workspace.
            </p>

            <div className="mt-8 space-y-4">
              <div className="flex items-center gap-3 text-sm text-muted-foreground">
                <ShieldCheck className="h-4 w-4 text-primary" />
                Enterprise-grade security, access controls, and audit-ready operations
              </div>
              <div className="flex items-center gap-3 text-sm text-muted-foreground">
                <LineChart className="h-4 w-4 text-primary" />
                Unified member intelligence, campaign orchestration, and ROI visibility
              </div>
              <div className="flex items-center gap-3 text-sm text-muted-foreground">
                <LockKeyhole className="h-4 w-4 text-primary" />
                Built for modern loyalty stacks with API-first, white-label flexibility
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
                  {mode === "signup" ? "Create your workspace" : "Welcome back"}
                </div>
                <div className="font-semibold text-foreground">Asteria Growth Cloud</div>
              </div>
            </div>
            <h2 className="text-2xl font-semibold text-foreground">
              {mode === "signup" ? "Create your loyalty operations account" : "Sign in to your loyalty workspace"}
            </h2>
            <p className="mt-2 text-sm text-muted-foreground">
              {mode === "signup"
                ? "Set up your account to launch campaigns, monitor member behavior, and review AI recommendations."
                : "Use your work credentials to access campaigns, analytics, and member operations."}
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            {mode === "signup" && (
              <>
                <div className="space-y-2">
                  <label className="text-sm font-medium text-foreground" htmlFor="fullName">Full Name</label>
                  <Input
                    id="fullName"
                    type="text"
                    autoComplete="name"
                    placeholder="Jane Patel"
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                    className="h-11"
                  />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium text-foreground" htmlFor="company">Company</label>
                  <Input
                    id="company"
                    type="text"
                    autoComplete="organization"
                    placeholder="Acme Loyalty Co"
                    value={company}
                    onChange={(e) => setCompany(e.target.value)}
                    className="h-11"
                  />
                </div>
              </>
            )}

            <div className="space-y-2">
              <label className="text-sm font-medium text-foreground" htmlFor="email">Work Email</label>
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
              <div className="relative">
                <Input
                  id="password"
                  type={showPassword ? "text" : "password"}
                  autoComplete={mode === "signup" ? "new-password" : "current-password"}
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  className="h-11 pr-10"
                />
                <button
                  type="button"
                  aria-label={showPassword ? "Hide password" : "Show password"}
                  onClick={() => setShowPassword((prev) => !prev)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                >
                  {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                </button>
              </div>
            </div>

            {mode === "signup" && password.length > 0 && (
              <div className="rounded-lg border border-border/60 bg-muted/20 px-3 py-2">
                <div className="mb-2 flex items-center justify-between text-xs text-muted-foreground">
                  <span>Password strength</span>
                  <span className="font-medium">{passwordStrength.label}</span>
                </div>
                <div className="mb-2 grid grid-cols-4 gap-1">
                  {[0, 1, 2, 3].map((idx) => (
                    <div
                      key={idx}
                      className={`h-1.5 rounded ${idx < passwordStrength.score ? passwordStrength.tone : "bg-muted"}`}
                    />
                  ))}
                </div>
                <div className="text-xs text-muted-foreground">
                  Use at least 8 characters, including uppercase, lowercase, and a number.
                </div>
              </div>
            )}

            {mode === "signup" && (
              <div className="space-y-2">
                <label className="text-sm font-medium text-foreground" htmlFor="confirmPassword">Confirm Password</label>
                <div className="relative">
                  <Input
                    id="confirmPassword"
                    type={showConfirmPassword ? "text" : "password"}
                    autoComplete="new-password"
                    placeholder="••••••••"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    required
                    className="h-11 pr-10"
                  />
                  <button
                    type="button"
                    aria-label={showConfirmPassword ? "Hide confirm password" : "Show confirm password"}
                    onClick={() => setShowConfirmPassword((prev) => !prev)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                  >
                    {showConfirmPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                  </button>
                </div>
              </div>
            )}

            {mode === "signup" && (
              <label className="flex items-start gap-2 rounded-lg border border-border/60 bg-muted/20 px-3 py-2 text-xs text-muted-foreground">
                <input
                  type="checkbox"
                  className="mt-0.5 h-4 w-4 accent-primary"
                  checked={acceptLegal}
                  onChange={(e) => setAcceptLegal(e.target.checked)}
                />
                <span>
                  I agree to the <Link to="/terms" className="text-primary hover:underline">Terms of Service</Link> and <Link to="/privacy" className="text-primary hover:underline">Privacy Policy</Link>.
                </span>
              </label>
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
                  {mode === "signup" ? "Create Workspace" : "Continue to Dashboard"}
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
                Forgot your password?
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
                    setAcceptLegal(false);
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
                    setAcceptLegal(false);
                  }}
                >
                  Sign in
                </button>
              </>
            )}
          </div>

          <p className="mt-3 text-xs text-muted-foreground">
            Secure sign-in is managed with token rotation and protected sessions.
          </p>
        </div>
      </div>
    </div>
  );
}
