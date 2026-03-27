import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { ArrowRight } from "lucide-react";
import { useAuth } from "@/contexts/AuthContext";
import { Button } from "@/components/ui/button";

export default function Login() {
  const navigate = useNavigate();
  const { quickLogin, isAuthenticated } = useAuth();
  const [isLoading, setIsLoading] = useState(false);

  // Redirect if already authenticated
  useEffect(() => {
    if (isAuthenticated) {
      navigate("/ai");
    }
  }, [isAuthenticated, navigate]);

  const handleQuickLogin = async () => {
    setIsLoading(true);

    try {
      await quickLogin();
      navigate("/ai");
    } catch (err) {
      console.error("Login failed:", err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-4">
      <div className="login-card w-full max-w-md animate-fade-in">
        {/* Logo */}
        <div className="mb-8 flex justify-center">
          <div className="w-16 h-16 bg-primary rounded-xl flex items-center justify-center shadow-lg">
            <span className="text-primary-foreground font-bold text-3xl">L</span>
          </div>
        </div>

        {/* Title */}
        <h1 className="text-3xl font-bold text-foreground mb-3 text-center">Loyalty Pro</h1>
        <p className="text-muted-foreground mb-12 text-center text-lg">
          Manager Portal Access
        </p>

        {/* Simple Sign In Button */}
        <Button
          onClick={handleQuickLogin}
          className="w-full h-12 text-lg"
          disabled={isLoading}
        >
          {isLoading ? (
            <>
              <div className="mr-2 h-5 w-5 animate-spin rounded-full border-2 border-background border-t-transparent" />
              Signing in...
            </>
          ) : (
            <>
              Sign In
              <ArrowRight className="ml-2 w-5 h-5" />
            </>
          )}
        </Button>

        {/* Info */}
        <div className="mt-8 p-4 bg-muted rounded-lg">
          <p className="text-sm text-muted-foreground text-center">
            Click the button above to access the loyalty management dashboard
          </p>
        </div>
      </div>
    </div>
  );
}
