import { PUBLIC_CRITINO_API_KEY } from '$env/static/public';
import { supabase, type Tables } from '$lib/supabase';
import critino from '$lib/apis/critino';

import { redirect } from '@sveltejs/kit';

export const load = async ({ locals: { safeGetSession, environment, auth } }) => {
	const { session } = await safeGetSession();

	if (!session) {
		console.log('No session found in /(menu)/dashboard');
		redirect(303, '/login');
	}

	const { data: submissions, error: eSubmissions } = await supabase
		.from('submissions')
		.select('*')
		.eq('profile_id', session.user.id)
		.order('created_at', { ascending: false });

	if (eSubmissions || !submissions) {
		console.error('Error loading submissions:', eSubmissions);
		return { status: 500, error: new Error('Failed to load leads') };
	}

	return { submissions };
};
