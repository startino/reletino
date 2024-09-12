import { supabase } from '$lib/supabase';


import type { Tables } from '$lib/supabase/database.types';

import { redirect } from '@sveltejs/kit';

export const load = async ({
  locals: { safeGetSession },
}) => {
  const { session } = await safeGetSession()
  
  if (!session) {
    redirect(303, "/login")
  }
	const { data, error } = await supabase.from('submissions').select('*').eq("is_relevant", true).order('created_at', { ascending: false });

  if (error || !data) {
    console.error("Error loading submissions:", error);
    return { status: 500, error: new Error('Failed to load leads') };
  }

	const relevantSubmissions = data as Tables<'submissions'>[];

	return { relevantSubmissions };
};