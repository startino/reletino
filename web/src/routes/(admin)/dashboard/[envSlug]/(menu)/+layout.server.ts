import type { Tables } from '$lib/supabase';
import { error, redirect } from '@sveltejs/kit';
import { getOrCreateEnvironment, getOrCreateProject } from '$lib/apis/critino';

export const load = async ({ locals: { safeGetSession, supabase, environment, auth }, params }) => {
	console.log('load in env slug menu');
	const { session } = await safeGetSession();

	if (!session) {
		console.log('No session found in /(menu)/dashboard');
		redirect(303, '/login');
	}

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

	const critinoEnvironment = async (env: Tables<'environments'>) => {
		if (environment.critino_key) {
			console.log('environment key already exists');
			return;
		}

		const key = await getOrCreateEnvironment(
			env.name,
			`env name: ${env.name}\nemail: ${auth.user?.email}\nuser id: ${auth.user?.id}`
		);

		if (!key) {
			throw error(500, 'Failed to create/update environment key');
		}

		const { error: eEnvironment } = await supabase
			.from('environments')
			.update({ critino_key: key })
			.eq('name', env.name);

		if (eEnvironment) {
			console.error(`Error updating environment: ${JSON.stringify(eEnvironment, null, 2)}`);
			throw error(500, 'Failed to update environment');
		}

		environment.critino_key = key;
	};

	await critinoEnvironment(environment);

	const { data: projects, error: eProjects } = await supabase
		.from('projects')
		.select('*')
		.eq('profile_id', session.user.id);

	if (eProjects || !projects) {
		console.error('Error loading submissions:', eProjects);
		throw error(500, 'Failed to load leads');
	}

	for (const project of projects) {
		const key = await getOrCreateProject(
			project.title,
			environment.name,
			`proj name: ${project.title}\nemail: ${auth.user?.email}\nuser id: ${auth.user?.id}`
		);

		if (key) {
			environment.critino_key = key;
		}
	}

	return {
		projects,
		usage,
	};
};
