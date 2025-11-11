import { createContext, useContext, useEffect, useState } from 'react'
import { authService } from '../services/authService'
import type { User, AuthState, SignInCredentials } from '../types'

interface AuthContextValue extends AuthState {
  signIn: (credentials: SignInCredentials) => Promise<void>
  signInWithGoogle: () => Promise<void>
  signOut: () => Promise<void>
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [state, setState] = useState<AuthState>({
    user: null,
    isLoading: true,
    error: null,
  })

  useEffect(() => {
    // Check for existing session
    authService.getCurrentUser().then(user => {
      setState({ user, isLoading: false, error: null })
    }).catch(() => {
      setState({ user: null, isLoading: false, error: null })
    })

    // Listen for auth changes
    const { data: { subscription } } = authService.onAuthStateChange(user => {
      setState(prev => ({ ...prev, user }))
    })

    return () => subscription.unsubscribe()
  }, [])

  const signIn = async (credentials: SignInCredentials) => {
    setState(prev => ({ ...prev, isLoading: true, error: null }))
    try {
      const user = await authService.signIn(credentials)
      setState({ user, isLoading: false, error: null })
    } catch (error) {
      setState({ user: null, isLoading: false, error: error.message })
      throw error
    }
  }

  const signInWithGoogle = async () => {
    setState(prev => ({ ...prev, isLoading: true, error: null }))
    try {
      await authService.signInWithGoogle()
      // OAuth redirect happens automatically, no setState needed
    } catch (error) {
      setState({ user: null, isLoading: false, error: error.message })
      throw error
    }
  }

  const signOut = async () => {
    setState(prev => ({ ...prev, isLoading: true }))
    try {
      await authService.signOut()
      setState({ user: null, isLoading: false, error: null })
    } catch (error) {
      setState(prev => ({ ...prev, isLoading: false, error: error.message }))
      throw error
    }
  }

  return (
    <AuthContext.Provider value={{ ...state, signIn, signInWithGoogle, signOut }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider')
  }
  return context
}