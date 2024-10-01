import type { Session, User } from "@supabase/supabase-js"
import { setContext, getContext } from "svelte"

const ENVIRONMENT_KEY = Symbol("AUTH")

export const setAuthState = (data: {
  session: Session | null
  user: User | null
}) => {
  const state = $state(data)
  return setContext(ENVIRONMENT_KEY, state)
}

export const getAuthState = () =>
  getContext<ReturnType<typeof setAuthState>>(ENVIRONMENT_KEY)
