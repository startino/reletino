import { error } from '@sveltejs/kit';

export const load = async ({ locals: { supabase, environment, auth }, params }) => {
	const { data, error: err } = await supabase
		.from('environments')
		.select('id')
		.eq('slug', params.envSlug)
		.single();

	if (err) {
		console.log({ err });

		if (err.code === 'PGRST116') {
			return error(404, 'Page not found');
		} else {
			return error(500);
		}
	}

	if (data.id !== environment?.id) {
		console.log({ data, environment });

		return error(404);
	}

	const { data: usage, error: eUsage } = await supabase
		.from('usage')
		.select('*')
		.eq('profile_id', auth.user?.id as string)
		.single();

	if (eUsage || !usage) {
		console.error('Error loading credits:', eUsage);
		return { status: 500, error: new Error('Failed to load credits') };
	}

	return {
		usage,
	};
};
