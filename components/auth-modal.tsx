"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Eye, EyeOff, Shield, Mail, User, Lock } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";

// Form schemas
const loginSchema = z.object({
  username: z.string().min(1, "Username is required"),
  password: z.string().min(1, "Password is required"),
});

const signupSchema = z.object({
  username: z.string().min(3, "Username must be at least 3 characters"),
  email: z.string().email("Invalid email address"),
  password: z.string().min(8, "Password must be at least 8 characters"),
  firstName: z.string().optional(),
  lastName: z.string().optional(),
});

type LoginForm = z.infer<typeof loginSchema>;
type SignupForm = z.infer<typeof signupSchema>;

interface AuthModalProps {
  isOpen: boolean;
  onClose: () => void;
  mode: "login" | "signup";
  onModeChange: (mode: "login" | "signup") => void;
}

export function AuthModal({ isOpen, onClose, mode, onModeChange }: AuthModalProps) {
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const router = useRouter();

  const loginForm = useForm<LoginForm>({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      username: "",
      password: "",
    },
  });

  const signupForm = useForm<SignupForm>({
    resolver: zodResolver(signupSchema),
    defaultValues: {
      username: "",
      email: "",
      password: "",
      firstName: "",
      lastName: "",
    },
  });

  const handleLogin = async (data: LoginForm) => {
    setIsLoading(true);
    setError("");

    try {
      const response = await fetch("http://localhost:8000/api/auth/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Login failed");
      }

      const result = await response.json();

      // Store token and user data
      localStorage.setItem("access_token", result.access_token);
      localStorage.setItem("user", JSON.stringify(result.user));

      // Reset form
      loginForm.reset();

      // Close modal and redirect
      onClose();
      router.push("/dashboard");
    } catch (err) {
      if (err instanceof Error) {
        // Handle specific error cases
        if (err.message.includes("fetch")) {
          setError("Cannot connect to server. Please ensure the backend is running on port 8000.");
        } else {
          setError(err.message);
        }
      } else {
        setError("Login failed. Please try again.");
      }
    } finally {
      setIsLoading(false);
    }
  };
  const handleSignup = async (data: SignupForm) => {
    setIsLoading(true);
    setError("");

    try {
      const response = await fetch("http://localhost:8000/api/auth/register", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          username: data.username,
          email: data.email,
          password: data.password,
          first_name: data.firstName,
          last_name: data.lastName,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Registration failed");
      }

      const result = await response.json();

      // Store token and user data
      localStorage.setItem("access_token", result.access_token);
      localStorage.setItem("user", JSON.stringify(result.user));

      // Reset form
      signupForm.reset();

      // Close modal and redirect
      onClose();
      router.push("/dashboard");
    } catch (err) {
      if (err instanceof Error) {
        // Handle specific error cases
        if (err.message.includes("fetch")) {
          setError("Cannot connect to server. Please ensure the backend is running on port 8000.");
        } else {
          setError(err.message);
        }
      } else {
        setError("Registration failed. Please try again.");
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-md bg-gray-900 border-green-500/30 text-green-400 font-mono">
        <DialogHeader>
          <div className="flex items-center justify-center space-x-2 mb-4">
            <div className="flex space-x-1">
              <div className="w-3 h-3 bg-red-500 rounded-full"></div>
              <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
              <div className="w-3 h-3 bg-green-500 rounded-full"></div>
            </div>
          </div>
          <DialogTitle className="text-xl font-bold text-center text-green-400">root@edos-shield: ~/{mode}</DialogTitle>
        </DialogHeader>

        <Card className="border-green-500/30 bg-black/50">
          <CardHeader className="text-center">
            <CardTitle className="text-lg font-mono text-white">
              {mode === "login" ? "$ ./authenticate" : "$ ./register --new-user"}
            </CardTitle>
            <CardDescription className="text-green-300 font-mono text-sm">
              {mode === "login" ? "# Accessing secure terminal session" : "# Creating new security clearance"}
            </CardDescription>
          </CardHeader>

          <CardContent className="space-y-4">
            {error && (
              <Badge
                variant="destructive"
                className="w-full justify-center py-2 font-mono bg-red-500/20 text-red-300 border-red-500/30"
              >
                [ERROR] {error}
              </Badge>
            )}

            {mode === "login" ? (
              <form onSubmit={loginForm.handleSubmit(handleLogin)} className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="username" className="text-green-400 font-mono text-sm">
                    --username
                  </Label>
                  <div className="relative">
                    <span className="absolute left-3 top-3 text-green-500 font-mono text-sm">$</span>
                    <Input
                      id="username"
                      placeholder="root"
                      className="pl-8 bg-black border-green-500/30 text-green-400 placeholder:text-green-600 font-mono focus:border-green-500"
                      {...loginForm.register("username")}
                    />
                  </div>
                  {loginForm.formState.errors.username && (
                    <p className="text-sm text-red-400 font-mono"># {loginForm.formState.errors.username.message}</p>
                  )}
                </div>

                <div className="space-y-2">
                  <Label htmlFor="password" className="text-green-400 font-mono text-sm">
                    --password
                  </Label>
                  <div className="relative">
                    <span className="absolute left-3 top-3 text-green-500 font-mono text-sm">$</span>
                    <Input
                      id="password"
                      type={showPassword ? "text" : "password"}
                      placeholder="••••••••"
                      className="pl-8 pr-10 bg-black border-green-500/30 text-green-400 placeholder:text-green-600 font-mono focus:border-green-500"
                      {...loginForm.register("password")}
                    />
                    <Button
                      type="button"
                      variant="ghost"
                      size="sm"
                      className="absolute right-0 top-0 h-full px-3 text-green-500 hover:text-green-400"
                      onClick={() => setShowPassword(!showPassword)}
                    >
                      {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                    </Button>
                  </div>
                  {loginForm.formState.errors.password && (
                    <p className="text-sm text-red-400 font-mono"># {loginForm.formState.errors.password.message}</p>
                  )}
                </div>

                <Button
                  type="submit"
                  className="w-full bg-green-500 text-black hover:bg-green-400 font-mono font-bold"
                  disabled={isLoading}
                >
                  {isLoading ? "$ authenticating..." : "$ execute --login"}
                </Button>
              </form>
            ) : (
              <form onSubmit={signupForm.handleSubmit(handleSignup)} className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="firstName" className="text-green-400 font-mono text-sm">
                      --first-name
                    </Label>
                    <Input
                      id="firstName"
                      placeholder="John"
                      className="bg-black border-green-500/30 text-green-400 placeholder:text-green-600 font-mono focus:border-green-500"
                      {...signupForm.register("firstName")}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="lastName" className="text-green-400 font-mono text-sm">
                      --last-name
                    </Label>
                    <Input
                      id="lastName"
                      placeholder="Doe"
                      className="bg-black border-green-500/30 text-green-400 placeholder:text-green-600 font-mono focus:border-green-500"
                      {...signupForm.register("lastName")}
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="username" className="text-green-400 font-mono text-sm">
                    --username
                  </Label>
                  <div className="relative">
                    <span className="absolute left-3 top-3 text-green-500 font-mono text-sm">$</span>
                    <Input
                      id="username"
                      placeholder="security_analyst"
                      className="pl-8 bg-black border-green-500/30 text-green-400 placeholder:text-green-600 font-mono focus:border-green-500"
                      {...signupForm.register("username")}
                    />
                  </div>
                  {signupForm.formState.errors.username && (
                    <p className="text-sm text-red-400 font-mono"># {signupForm.formState.errors.username.message}</p>
                  )}
                </div>

                <div className="space-y-2">
                  <Label htmlFor="email" className="text-green-400 font-mono text-sm">
                    --email
                  </Label>
                  <div className="relative">
                    <span className="absolute left-3 top-3 text-green-500 font-mono text-sm">@</span>
                    <Input
                      id="email"
                      type="email"
                      placeholder="admin@security.com"
                      className="pl-8 bg-black border-green-500/30 text-green-400 placeholder:text-green-600 font-mono focus:border-green-500"
                      {...signupForm.register("email")}
                    />
                  </div>
                  {signupForm.formState.errors.email && (
                    <p className="text-sm text-red-400 font-mono"># {signupForm.formState.errors.email.message}</p>
                  )}
                </div>

                <div className="space-y-2">
                  <Label htmlFor="password" className="text-green-400 font-mono text-sm">
                    --password
                  </Label>
                  <div className="relative">
                    <span className="absolute left-3 top-3 text-green-500 font-mono text-sm">$</span>
                    <Input
                      id="password"
                      type={showPassword ? "text" : "password"}
                      placeholder="••••••••••••"
                      className="pl-8 pr-10 bg-black border-green-500/30 text-green-400 placeholder:text-green-600 font-mono focus:border-green-500"
                      {...signupForm.register("password")}
                    />
                    <Button
                      type="button"
                      variant="ghost"
                      size="sm"
                      className="absolute right-0 top-0 h-full px-3 text-green-500 hover:text-green-400"
                      onClick={() => setShowPassword(!showPassword)}
                    >
                      {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                    </Button>
                  </div>
                  {signupForm.formState.errors.password && (
                    <p className="text-sm text-red-400 font-mono"># {signupForm.formState.errors.password.message}</p>
                  )}
                </div>

                <Button
                  type="submit"
                  className="w-full bg-green-500 text-black hover:bg-green-400 font-mono font-bold"
                  disabled={isLoading}
                >
                  {isLoading ? "$ creating user..." : "$ execute --register"}
                </Button>
              </form>
            )}

            <div className="text-center text-sm border-t border-green-500/30 pt-4">
              <span className="text-green-500 font-mono">
                {mode === "login" ? "# No clearance? " : "# Already authenticated? "}
              </span>
              <Button
                variant="link"
                className="p-0 text-green-400 hover:text-green-300 font-mono underline"
                onClick={() => onModeChange(mode === "login" ? "signup" : "login")}
              >
                ./{mode === "login" ? "register" : "login"}
              </Button>
            </div>
          </CardContent>
        </Card>
      </DialogContent>
    </Dialog>
  );
}
