import { useState } from 'react';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Checkbox } from '../ui/checkbox';
import { Separator } from '../ui/separator';
import { Loader2, AlertCircle } from 'lucide-react';

interface LoginProps {
  onLogin: (token: string) => void;
  onSwitchToRegister: () => void;
}

export function Login({ onLogin, onSwitchToRegister }: LoginProps) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  
  // Logic states
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await fetch('http://localhost:8080/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });

      const data = await response.json();

      if (response.ok) {
        onLogin(data.token); // Pass the token up to App.tsx
      } else {
        setError('Invalid email or password');
      }
    } catch (err) {
      setError('Server error. Is the backend running?');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen">
      {/* Left Side - Image */}
      <div className="hidden lg:flex lg:w-1/2 relative bg-slate-900">
        <img
          src="https://images.unsplash.com/photo-1760626301131-b12379ceaf43?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxtb2Rlcm4lMjBjb25uZWN0ZWQlMjB2ZWhpY2xlJTIwY2l0eXxlbnwxfHx8fDE3NjU1NDU2MjV8MA&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral"
          alt="Modern connected vehicle"
          className="object-cover w-full h-full opacity-80"
        />
        <div className="absolute inset-0 bg-gradient-to-r from-blue-900/40 to-purple-900/40" />
        <div className="absolute bottom-12 left-12 text-white max-w-lg">
          <h2 className="text-4xl mb-4 font-bold">Intelligent Automotive Intelligence</h2>
          <p className="text-lg opacity-90">
            AI-powered orchestration for predictive maintenance, quality insights, and autonomous service management.
          </p>
        </div>
      </div>

      {/* Right Side - Login Form */}
      <div className="w-full lg:w-1/2 flex items-center justify-center bg-white p-8">
        <div className="w-full max-w-md">
          <div className="mb-8">
            <h1 className="text-3xl font-bold mb-2">OEM Aftersales Intelligence Portal</h1>
            <p className="text-slate-600">Sign in to access your command center</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <Label htmlFor="email">Email Address</Label>
              <Input
                id="email"
                type="email"
                placeholder="your.email@company.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="mt-1"
                required
              />
            </div>

            <div>
              <Label htmlFor="password">Password</Label>
              <Input
                id="password"
                type="password"
                placeholder="Enter your password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="mt-1"
                required
              />
            </div>

            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <Checkbox id="remember" />
                <label htmlFor="remember" className="text-sm cursor-pointer text-slate-600">
                  Remember me
                </label>
              </div>
              <button type="button" className="text-sm text-blue-600 hover:underline">
                Forgot password?
              </button>
            </div>

            {/* Error Message Display */}
            {error && (
                <div className="flex items-center space-x-2 text-red-600 bg-red-50 p-3 rounded-md text-sm">
                <AlertCircle className="w-4 h-4" />
                <span>{error}</span>
                </div>
            )}

            <Button type="submit" className="w-full" disabled={loading}>
                {loading ? (
                    <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        Signing in...
                    </>
                ) : (
                    'Sign In'
                )}
            </Button>
          </form>

          <div className="mt-6">
            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <Separator />
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="bg-white px-2 text-slate-500">Or continue with</span>
              </div>
            </div>

            <div className="mt-6 grid grid-cols-2 gap-3">
              <Button variant="outline" type="button">
                <svg className="w-5 h-5 mr-2" viewBox="0 0 24 24">
                  <path
                    fill="currentColor"
                    d="M23.766 12.276c0-.815-.07-1.601-.205-2.357H12.24v4.456h6.486a5.54 5.54 0 0 1-2.405 3.638v2.966h3.893c2.278-2.095 3.552-5.18 3.552-8.703z"
                  />
                  <path
                    fill="currentColor"
                    d="M12.24 24c3.254 0 5.982-1.076 7.977-2.92l-3.893-2.967c-1.08.724-2.463 1.15-4.084 1.15-3.142 0-5.805-2.122-6.754-4.975H1.38v3.063A11.996 11.996 0 0 0 12.24 24z"
                  />
                  <path
                    fill="currentColor"
                    d="M5.486 14.288a7.203 7.203 0 0 1 0-4.576V6.649H1.38a11.996 11.996 0 0 0 0 10.702l4.106-3.063z"
                  />
                  <path
                    fill="currentColor"
                    d="M12.24 4.737c1.773 0 3.362.61 4.613 1.804l3.458-3.457C18.217 1.19 15.49 0 12.24 0A11.996 11.996 0 0 0 1.38 6.649l4.106 3.063c.95-2.853 3.612-4.975 6.754-4.975z"
                  />
                </svg>
                Google
              </Button>
              <Button variant="outline" type="button">
                <svg className="w-5 h-5 mr-2" viewBox="0 0 24 24">
                  <path
                    fill="currentColor"
                    d="M23.5 12.3c0-6.4-5.2-11.6-11.6-11.6S.3 5.9.3 12.3c0 5.8 4.2 10.5 9.7 11.4V15.8H7.4v-3.5H10V9.8c0-2.6 1.5-4 3.9-4 1.1 0 2.3.2 2.3.2v2.5h-1.3c-1.3 0-1.7.8-1.7 1.6v1.9h2.8l-.4 3.5h-2.4v7.9c5.5-.9 9.7-5.6 9.7-11.4z"
                  />
                </svg>
                Microsoft
              </Button>
            </div>
          </div>

          <div className="mt-8 text-center">
            <p className="text-sm text-slate-600">
              Don't have an account?{' '}
              <button
                type="button"
                onClick={onSwitchToRegister}
                className="text-blue-600 hover:underline font-medium"
              >
                Register here
              </button>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}