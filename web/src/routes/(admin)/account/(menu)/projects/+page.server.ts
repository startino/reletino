import { supabase, type Tables } from "$lib/supabase";
import { redirect } from "@sveltejs/kit";

export const load = async ({
  locals: { safeGetSession },
}) => {
  const { session } = await safeGetSession()
  
  if (!session) {
    redirect(303, "/login")
  }

  console.log("profile_id", session.user.id);
  const { data, error } = await supabase.from('projects').select('*').eq("profile_id", session.user.id);

  if (error || !data) {
    console.error("Error loading submissions:", error);
    return { status: 500, error: new Error('Failed to load leads') };
  }

  const projects = data as Tables<'projects'>[];

  return {
    projects
  };
};

export const actions = {

}