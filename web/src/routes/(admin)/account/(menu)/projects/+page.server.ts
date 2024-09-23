import { projectSchema } from "$lib/schemas"
import { supabase, type Tables } from "$lib/supabase"
import { fail, redirect } from "@sveltejs/kit"
import { message, superValidate } from "sveltekit-superforms"
import { zod } from "sveltekit-superforms/adapters"
import { PUBLIC_API_URL } from "$env/static/public"

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

    // Used for telling the user if the server was able to start/stop the project
    let responseStatus: "success" | "error" = "error";
    
    if (form.data.running) {
      // Start the project
      await fetch(`${PUBLIC_API_URL}/start`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          ...form.data
        }),
      }).then((res) => res.json()).then((data) => responseStatus = data.status)
    } else {
      // Stop the project
      await fetch(`${PUBLIC_API_URL}/stop`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          "project_id": form.data.id
        }),
      }).then((res) => res.json()).then((data) => responseStatus = data.status)
    }

    if (responseStatus == "error") {
      return message(form, { type: "error", text: "Our server couldn't fulfill your request. Try again or contact me: jorge.lewis@starti.no" })
    }

    const { data, error, status } = await supabase
    .from("projects")
    .upsert({
      ...form.data,
    })
    .select()

    if (status == 201) {
      return message(form, { type: "success", text: "Project Created!" })
    }
    else if (status == 200) {
      return message(form, { type: "success", text: "Project Updated!" })
    }

    if (error || !data) {
      return message(form, {
        type: "error",
        text: "Error occured when saving project.",
      })
    }

    return message(form, { type: "success", text: "Project Updated!" })
  },
}
