import { createClient } from '@supabase/supabase-js'
import type { User, SignInCredentials } from '../types'

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL || ''
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY || ''

export const supabase = createClient(supabaseUrl, supabaseAnonKey)

export const authService = {
  async signIn(credentials: SignInCredentials): Promise<User> {
    const { data, error } = await supabase.auth.signInWithPassword({
      email: credentials.email,
      password: credentials.password,
    })

    if (error) throw error
    if (!data.user) throw new Error('No user returned')

    return {
      id: data.user.id,
      email: data.user.email!,
      name: data.user.user_metadata?.name,
      avatar: data.user.user_metadata?.avatar_url,
    }
  },

  async signOut(): Promise<void> {
    const { error } = await supabase.auth.signOut()
    if (error) throw error
  },

  async getCurrentUser(): Promise<User | null> {
    const { data: { user } } = await supabase.auth.getUser()
    
    if (!user) return null

    return {
      id: user.id,
      email: user.email!,
      name: user.user_metadata?.name,
      avatar: user.user_metadata?.avatar_url,
    }
  },

  onAuthStateChange(callback: (user: User | null) => void) {
    return supabase.auth.onAuthStateChange((event, session) => {
      if (session?.user) {
        callback({
          id: session.user.id,
          email: session.user.email!,
          name: session.user.user_metadata?.name,
          avatar: session.user.user_metadata?.avatar_url,
        })
      } else {
        callback(null)
      }
    })
  }
}