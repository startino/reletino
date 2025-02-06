import type { PostgrestError } from '@supabase/supabase-js';
import { error } from '@sveltejs/kit';

export const load = async ({ params: { id }, locals: { supabase, safeGetSession } }) => {
	const { session } = await safeGetSession();
	const userId = session!.user.id;
	try {
		const { data: project, error: projectError } = await supabase
			.from('projects')
			.select('*')
			.eq('id', id)
			.eq('profile_id', userId)
			.single();

		if (projectError) {
			console.warn('Error fetching project: ', projectError);
			throw projectError;
		}

		const { data: submissions, error: submissionsError } = await supabase
			.from('submissions')
			.select('*')
			.eq('profile_id', userId)
			.eq('project_id', id)
			.order('created_at', { ascending: false });

		if (submissionsError) {
			console.warn('Error fetching submissions: ', submissionsError);
			throw submissionsError;
		}

		return { project, submissions };
	} catch (err) {
		const postgrestError = err as PostgrestError;

		if (postgrestError.code === 'PGRST116') {
			return error(404, 'Page not found');
		} else {
			return error(500);
		}
	}
};
