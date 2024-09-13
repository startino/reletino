import { projectSchema } from "$lib/schemas"
import { supabase, type Tables } from "$lib/supabase"
import { redirect } from "@sveltejs/kit"
import { superValidate } from "sveltekit-superforms"
import { zod } from "sveltekit-superforms/adapters"

export const load = async ({ locals: { safeGetSession } }) => {
  const { session } = await safeGetSession()

  if (!session) {
    redirect(303, "/login")
  }

  console.log("profile_id", session.user.id)
  const { data, error } = await supabase
    .from("projects")
    .select("*")
    .eq("profile_id", session.user.id)

  if (error || !data) {
    console.error("Error loading submissions:", error)
    return { status: 500, error: new Error("Failed to load leads") }
  }

  const projects = data as Tables<"projects">[]

  return {
    projectForm: await superValidate(zod(projectSchema)),
    projects,
  }
}

export const actions = {}
