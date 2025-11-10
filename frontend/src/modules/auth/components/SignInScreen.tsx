import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Brain, Eye, EyeOff, Loader2 } from 'lucide-react'
import { useAuth } from '../contexts/AuthContext'
import type { SignInCredentials } from '../types'

export function SignInScreen() {
  const navigate = useNavigate()
  const { signIn, isLoading, error } = useAuth()
  const [showPassword, setShowPassword] = useState(false)
  const [credentials, setCredentials] = useState<SignInCredentials>({
    email: '',
    password: ''
  })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      await signIn(credentials)
      navigate('/dashboard')
    } catch (err) {
      // Error is handled by AuthContext
    }
  }

  const isValid = credentials.email && credentials.password

  return (
    <div className="min-h-screen bg-white flex">
      {/* Left side - Sign in form */}
      <div className="flex-1 flex flex-col justify-center px-8 sm:px-12 lg:px-16">
        <div className="w-full max-w-md mx-auto">
          {/* Logo and Title */}
          <div className="mb-8">
            <div className="flex items-center space-x-3 mb-6">
              <div className="w-10 h-10 bg-black rounded-full flex items-center justify-center">
                <Brain className="w-5 h-5 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-semibold text-black">GVSES</h1>
                <p className="text-sm text-gray-500">AI Market Analysis Assistant</p>
              </div>
            </div>
            <h2 className="text-3xl font-light text-gray-900">Welcome back</h2>
            <p className="mt-2 text-sm text-gray-600">
              Sign in to access your AI-powered trading assistant
            </p>
          </div>

          {/* Error Alert */}
          {error && (
            <Alert variant="destructive" className="mb-6">
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          {/* Sign in form */}
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <Label htmlFor="email" className="text-sm font-medium text-gray-700">
                Email address
              </Label>
              <Input
                id="email"
                type="email"
                autoComplete="email"
                required
                value={credentials.email}
                onChange={(e) => setCredentials(prev => ({ ...prev, email: e.target.value }))}
                className="mt-1"
                placeholder="you@example.com"
              />
            </div>

            <div>
              <Label htmlFor="password" className="text-sm font-medium text-gray-700">
                Password
              </Label>
              <div className="relative mt-1">
                <Input
                  id="password"
                  type={showPassword ? 'text' : 'password'}
                  autoComplete="current-password"
                  required
                  value={credentials.password}
                  onChange={(e) => setCredentials(prev => ({ ...prev, password: e.target.value }))}
                  className="pr-10"
                  placeholder="Enter your password"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute inset-y-0 right-0 flex items-center pr-3 text-gray-400 hover:text-gray-600"
                >
                  {showPassword ? (
                    <EyeOff className="w-4 h-4" />
                  ) : (
                    <Eye className="w-4 h-4" />
                  )}
                </button>
              </div>
            </div>

            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <input
                  id="remember-me"
                  name="remember-me"
                  type="checkbox"
                  className="h-4 w-4 rounded border-gray-300 text-green-600 focus:ring-green-500"
                />
                <label htmlFor="remember-me" className="ml-2 block text-sm text-gray-700">
                  Remember me
                </label>
              </div>

              <div className="text-sm">
                <Link to="/forgot-password" className="font-medium text-green-600 hover:text-green-500">
                  Forgot your password?
                </Link>
              </div>
            </div>

            <Button
              type="submit"
              disabled={!isValid || isLoading}
              className="w-full bg-green-600 hover:bg-green-700 text-white"
            >
              {isLoading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Signing in...
                </>
              ) : (
                'Sign in'
              )}
            </Button>
          </form>

          {/* Demo mode */}
          <div className="mt-6">
            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-gray-300" />
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="bg-white px-2 text-gray-500">Or continue with</span>
              </div>
            </div>

            <div className="mt-6">
              <Button
                type="button"
                variant="outline"
                className="w-full"
                onClick={() => navigate('/demo')}
              >
                Try Demo Mode
              </Button>
            </div>
          </div>

          {/* Sign up link */}
          <p className="mt-8 text-center text-sm text-gray-600">
            Don't have an account?{' '}
            <Link to="/signup" className="font-medium text-green-600 hover:text-green-500">
              Sign up for free
            </Link>
          </p>
        </div>
      </div>

      {/* Right side - Feature highlights */}
      <div className="hidden lg:block relative flex-1 bg-gray-50">
        <div className="absolute inset-0 flex items-center justify-center p-16">
          <div className="max-w-lg">
            <h3 className="text-2xl font-light text-gray-900 mb-6">
              AI-Powered Market Analysis
            </h3>
            <div className="space-y-4">
              <div className="flex items-start space-x-3">
                <div className="w-2 h-2 bg-green-500 rounded-full mt-2" />
                <div>
                  <p className="text-gray-700 font-medium">Real-time Chart Analysis</p>
                  <p className="text-sm text-gray-600">
                    Voice-controlled interactive charts with pattern recognition
                  </p>
                </div>
              </div>
              <div className="flex items-start space-x-3">
                <div className="w-2 h-2 bg-green-500 rounded-full mt-2" />
                <div>
                  <p className="text-gray-700 font-medium">GVSES Trading Levels</p>
                  <p className="text-sm text-gray-600">
                    Proprietary LTB, ST, and QE levels for optimal entry points
                  </p>
                </div>
              </div>
              <div className="flex items-start space-x-3">
                <div className="w-2 h-2 bg-green-500 rounded-full mt-2" />
                <div>
                  <p className="text-gray-700 font-medium">Educational Insights</p>
                  <p className="text-sm text-gray-600">
                    Learn market patterns and technical analysis through AI guidance
                  </p>
                </div>
              </div>
            </div>
            <div className="mt-8 p-4 bg-white rounded-lg border border-gray-200">
              <p className="text-sm text-gray-600 italic">
                "GVSES has transformed how I analyze charts. The voice commands make it
                incredibly intuitive to explore different timeframes and patterns."
              </p>
              <p className="text-sm text-gray-700 font-medium mt-2">- Active Trader</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}