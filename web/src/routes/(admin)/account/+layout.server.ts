import type { LayoutServerLoad } from './$types'

export const load: LayoutServerLoad = async ({ locals: { supabase, safeGetSession }, cookies }) => {
  const { session } = await safeGetSession()
  
  let profile = null;
  if (session) {
    profile = (await supabase
      .from("profiles")
      .select(`*`)
      .eq("id", session.user.id)
      .single()).data.profile
  }

  return {
    session,
    profile,
    cookies: cookies.getAll(),
  }
}