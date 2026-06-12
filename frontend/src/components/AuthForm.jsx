import React, { useState } from "react";
import { Brain, LogIn, UserPlus } from "lucide-react";
import { GlowingCard } from "./ui/GlowingCard";
import { HoverBorderGradient } from "./ui/HoverBorderGradient";
import { apiFetch, setAuth } from "../lib/auth";

export function AuthForm({ onSuccess }) {
  const [mode, setMode] = useState("login");
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const path = mode === "login" ? "/auth/login" : "/auth/signup";
      const body = mode === "login" ? { email, password } : { name, email, password };
      const data = await apiFetch(path, { method: "POST", body: JSON.stringify(body) });
      setAuth(data.access_token, data.user);
      onSuccess(data.user);
    } catch (err) {
      setError(err.message || "Authentication failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center px-6 py-12">
      <div className="w-full max-w-md space-y-8">
        <div className="text-center space-y-3">
          <div className="inline-flex p-3 rounded-2xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-400">
            <Brain className="w-8 h-8" />
          </div>
          <h1 className="text-3xl font-extrabold text-zinc-100">InterviewerAI</h1>
          <p className="text-zinc-400 text-sm">Sign in to track your assessments and reports</p>
        </div>

        <GlowingCard>
          <form onSubmit={handleSubmit} className="space-y-4">
            {mode === "signup" && (
              <Input label="Full Name" value={name} onChange={setName} placeholder="Your name" required />
            )}
            <Input label="Email" type="email" value={email} onChange={setEmail} placeholder="you@example.com" required />
            <Input label="Password" type="password" value={password} onChange={setPassword} placeholder="••••••••" required />

            {error && <p className="text-xs text-red-400">{error}</p>}

            <HoverBorderGradient type="submit" containerClassName="w-full" disabled={loading}>
              <span className="flex items-center justify-center gap-2">
                {mode === "login" ? <LogIn className="w-4 h-4" /> : <UserPlus className="w-4 h-4" />}
                {loading ? "Please wait..." : mode === "login" ? "Sign In" : "Create Account"}
              </span>
            </HoverBorderGradient>
          </form>

          <p className="text-center text-xs text-zinc-500 mt-4">
            {mode === "login" ? "Don't have an account?" : "Already have an account?"}{" "}
            <button
              type="button"
              onClick={() => { setMode(mode === "login" ? "signup" : "login"); setError(""); }}
              className="text-indigo-400 hover:underline"
            >
              {mode === "login" ? "Sign up" : "Sign in"}
            </button>
          </p>
        </GlowingCard>
      </div>
    </div>
  );
}

function Input({ label, value, onChange, type = "text", placeholder, required }) {
  return (
    <div className="space-y-2">
      <label className="text-xs font-bold uppercase tracking-wider text-zinc-400 font-mono">{label}</label>
      <input
        type={type}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        required={required}
        className="w-full bg-zinc-900 border border-white/10 rounded-xl px-4 py-3 text-zinc-100 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
      />
    </div>
  );
}
