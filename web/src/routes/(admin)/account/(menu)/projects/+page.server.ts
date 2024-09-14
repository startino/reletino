import { projectSchema } from "$lib/schemas"
import { supabase, type Tables } from "$lib/supabase"
import { fail, redirect } from "@sveltejs/kit"
import { message, superValidate } from "sveltekit-superforms"
import { zod } from "sveltekit-superforms/adapters"

export const load = async ({ locals: { safeGetSession } }) => {
  const { session } = await safeGetSession()

  if (!session) {
    redirect(303, "/login")
  }

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

export const actions = {
  updateProject: async ({ request }) => {
    const form = await superValidate(request, zod(projectSchema))

    console.log("Updating project:", form.data)

    if (!form.valid) {
      return message(form, {
        type: "error",
        text: "Error occured when saving project.",
      })
    }

    const { data, error, status, statusText } = await supabase
      .from("projects")
      .upsert({
        ...form.data,
      })
      .select()

    console.log("Status:", status);
    console.log("Status Text:", statusText);

    if (error || !data) {
      return message(form, {
        type: "error",
        text: "Error occured when saving project.",
      })
    }

    return message(form, { type: "success", text: "Project Updated!" })
  },
}
