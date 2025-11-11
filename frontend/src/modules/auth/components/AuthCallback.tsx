import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Loader2 } from 'lucide-react'
import { useAuth } from '../contexts/AuthContext'

export function AuthCallback() {
  const navigate = useNavigate()
  const { user, isLoading } = useAuth()

  useEffect(() => {
    // Once the OAuth callback completes and the user is set,
    // redirect to dashboard (or the 'next' param if provided)
    if (!isLoading && user) {
      const params = new URLSearchParams(window.location.search)
      const next = params.get('next') || '/dashboard'
      navigate(next, { replace: true })
    }
  }, [isLoading, user, navigate])

  return (
    <div className="min-h-screen bg-white flex items-center justify-center">
      <div className="text-center">
        <Loader2 className="w-8 h-8 animate-spin text-black mx-auto mb-4" />
        <h2 className="text-lg font-medium text-gray-900">Signing you in...</h2>
        <p className="text-sm text-gray-600 mt-2">Please wait while we complete authentication</p>
      </div>
    </div>
  )
}
