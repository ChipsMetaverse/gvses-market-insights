export interface User {
  id: string
  email: string
  name?: string
  avatar?: string
}

export interface AuthState {
  user: User | null
  isLoading: boolean
  error: string | null
}

export interface SignInCredentials {
  email: string
  password: string
}