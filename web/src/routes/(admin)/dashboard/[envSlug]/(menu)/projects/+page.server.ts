import { redirect } from '@sveltejs/kit';

export const load = async ({ locals: { safeGetSession, supabase } }) => {
	const { session } = await safeGetSession();

	if (!session) {
		redirect(303, '/login');
	}

	const { data: projects, error } = await supabase
		.from('projects')
		.select('*')
		.eq('profile_id', session.user.id);

	if (error || !projects) {
		console.error('Error loading submissions:', error);
		return { status: 500, error: new Error('Failed to load leads') };
	}

	return {
		projects,
	};
};
