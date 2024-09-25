import { error } from "@sveltejs/kit"

export const load = async ({ locals: { supabase, safeGetSession } }) => {
  const { session, user } = await safeGetSession()

  const { data: profile, error: profileError } = await supabase
    .from("profiles")
    .select(`*`)
    .eq("id", session?.user.id as string)
    .single()

  if (profileError) {
    console.error({ profileError })
    if (profileError.code === "PGRST116") {
      return error(404, "Page not found")
    }
    return error(500, "Something went wrong")
  }

  return { session, profile, user }
}
