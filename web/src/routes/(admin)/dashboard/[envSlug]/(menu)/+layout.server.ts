import type { Tables } from '$lib/supabase';
import { error, redirect } from '@sveltejs/kit';
import critino from '$lib/apis/critino';
import { PUBLIC_CRITINO_API_KEY } from '$env/static/public';

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

	console.log('critino api key: ', PUBLIC_CRITINO_API_KEY);

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

	const { data: projects, error: eProjects } = await supabase
		.from('projects')
		.select('*')
		.eq('profile_id', session.user.id);

	if (eProjects || !projects) {
		console.error('Error loading submissions:', eProjects);
		return { status: 500, error: new Error('Failed to load leads') };
	}

	const getOrCreateCritinoProject = async (project: Tables<'projects'>) => {
		console.log('getOrCreateCritinoProject');
		const readResponse = await critino.GET('/environments/{name}', {
			params: {
				query: {
					team_name: 'startino',
					parent_name: 'reletino/' + environment?.name,
				},
				path: {
					name: project.title, // TODO: rename project title to project name
				},
				header: {
					'x-critino-key': PUBLIC_CRITINO_API_KEY,
				},
			},
		});
		console.log('readResponse', readResponse);

		if (readResponse.error) {
			console.log('getOrCreateCritinoProject error');
			const createResponse = await critino.POST('/environments/{name}', {
				params: {
					query: {
						team_name: 'startino',
						parent_name: 'reletino/' + environment?.name,
					},
					path: {
						name: project.title, // TODO: rename project title to project name
					},
					header: {
						'x-critino-key': PUBLIC_CRITINO_API_KEY,
					},
				},
				body: {
					gen_key: false,
					description: `proj name: ${project.title}\nemail: ${auth.user?.email}\nuser id: ${auth.user?.id}`, // TODO: rename project title to project name
				},
			});
			console.log('createResponse', createResponse);
		}

		console.log('getOrCreateCritinoProject end');
	};

	for (const project of projects) {
		await getOrCreateCritinoProject(project);
	}

	return {
		projects,
		usage,
	};
};
