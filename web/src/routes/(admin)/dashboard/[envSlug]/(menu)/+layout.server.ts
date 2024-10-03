import type { Tables } from '$lib/supabase';
import { error } from '@sveltejs/kit';
import critino from '$lib/apis/critino';
import { PUBLIC_CRITINO_API_KEY } from '$env/static/public';

export const load = async ({ locals: { supabase, environment, auth }, params }) => {
	console.log('load in env slug menu');
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

	const getOrCreateCritinoEnvironment = async (env: Tables<'environments'>) => {
		console.log('getOrCreateCritinoEnvironment');
		const readResponse = await critino.GET('/environments/{name}', {
			params: {
				query: {
					team_name: 'startino',
					parent_name: 'reletino',
				},
				path: {
					name: env.name,
				},
				header: {
					'x-critino-key': PUBLIC_CRITINO_API_KEY,
				},
			},
		});
		console.log('readResponse', readResponse);

		if (readResponse.error) {
			console.log('getOrCreateCritinoEnvironment error');
			const createResponse = await critino.POST('/environments/{name}', {
				params: {
					query: {
						team_name: 'startino',
						parent_name: 'reletino',
					},
					path: {
						name: env.name,
					},
					header: {
						'x-critino-key': PUBLIC_CRITINO_API_KEY,
					},
				},
				body: {
					gen_key: true,
					description: `env name: ${env.name}\nemail: ${auth.user?.email}\nuser id: ${auth.user?.id}`,
				},
			});
			console.log('createResponse', createResponse);
		}

		console.log('getOrCreateCritinoEnvironment end');
	};

	await getOrCreateCritinoEnvironment(environment);

	return {
		usage,
	};
};
