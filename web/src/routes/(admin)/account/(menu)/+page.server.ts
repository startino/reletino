import { supabase } from '$lib/supabase';

import { redirect } from '@sveltejs/kit';

export const load = async ({
  locals: { safeGetSession },
}) => {
  const { session } = await safeGetSession()
  
  if (!session) {
    redirect(303, "/login")
  }
	const { data: relevantSubmissions, error: eRelevantSubmissions } = await supabase.from('submissions').select('*').eq("is_relevant", true).order('created_at', { ascending: false });

  if (eRelevantSubmissions || !relevantSubmissions) {
    console.error("Error loading submissions:", eRelevantSubmissions);
    return { status: 500, error: new Error('Failed to load leads') };
  }
  
  const { data: projects ,  error: eProjects } = await supabase.from('projects').select('*').eq("profile_id", session.user.id);

  if (eProjects || !projects) {
    console.error("Error loading submissions:", eProjects);
    return { status: 500, error: new Error('Failed to load leads') };
  }

	return { projects, relevantSubmissions };
};