import { supabase } from "$lib/supabase"

import { redirect } from "@sveltejs/kit"

export const load = async ({ locals: { safeGetSession } }) => {
  const { session } = await safeGetSession()

  if (!session) {
    redirect(303, "/login")
  }
  const { data: submissions, error: eSubmissions } =
    await supabase
      .from("submissions")
      .select("*").eq("profile_id", session.user.id)
      .order("created_at", { ascending: false })

  if (eSubmissions || !submissions) {
    console.error("Error loading submissions:", eSubmissions)
    return { status: 500, error: new Error("Failed to load leads") }
  }

  const { data: projects, error: eProjects } = await supabase
    .from("projects")
    .select("*")
    .eq("profile_id", session.user.id)

  if (eProjects || !projects) {
    console.error("Error loading submissions:", eProjects)
    return { status: 500, error: new Error("Failed to load leads") }
  }

  return { projects, submissions }
}
