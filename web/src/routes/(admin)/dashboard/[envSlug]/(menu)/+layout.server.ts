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

	const getOrCreateEnvironment = async (env: Tables<'environments'>) => {
		if (environment.critino_key) {
		  console.log('environment key already exists');
		  return;
		}
		console.log('environment', environment);
	  
		const reletinoEnvironment = await critino.GET('/environments/{name}', {
		  params: {
			query: {
			  team_name: 'startino',
			  parent_name: 'reletino'
			},
			path: {
			  name: env.name
			},
			header: {
			  'x-critino-key': PUBLIC_CRITINO_API_KEY,
			},
		  },
		});

		console.log('reletinoEnvironment', reletinoEnvironment);
	  
		if (!reletinoEnvironment.error) {
		  const updateKeyResponse = await critino.PATCH('/environments/{name}/key', {
			params: {
			  query: {
				team_name: 'startino',
				parent_name: 'reletino'
			  },
			  path: {
				name: env.name
			  },
			  header: {
				'x-critino-key': PUBLIC_CRITINO_API_KEY,
			  },
			},
		  });

		  console.log('updateKeyResponse', updateKeyResponse);
	  
		  if (!updateKeyResponse.data || updateKeyResponse.error) {
			console.error(`Error updating environment key: ${JSON.stringify(updateKeyResponse.error, null, 2)}`);
			throw error(500, 'Failed to update environment key');
		  }
	  
		  const { error: eEnvironment } = await supabase
			.from('environments')
			.update({ critino_key: updateKeyResponse.data.key })
			.eq('name', env.name);
	  
		  console.log('error env', env.name, eEnvironment);
		  environment.critino_key = updateKeyResponse.data.key;
		  return;
		}
	  
		const newEnvironment = await critino.POST('/environments/{name}', {
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
				description: `env name: ${env.name}\nemail: ${auth.user?.email}\nuser id: ${auth.user?.id}`,
				gen_key: false
			},
		});

		console.log('newEnvironment', newEnvironment);

		if (!newEnvironment.data || newEnvironment.error) {
			console.error(
				`Error creating environment: ${JSON.stringify(newEnvironment.error, null, 2)}`
			);
			throw error(500, 'Failed to update environment key');
		}

		const { error: eEnvironment } = await supabase
			.from('environments')
			.update({ critino_key: newEnvironment.data.key })
			.eq('name', env.name);

		if (eEnvironment) {
			console.error(`Error updating environment: ${JSON.stringify(eEnvironment, null, 2)}`);
			throw error(500, 'Failed to update environment');
		}

		environment.critino_key = newEnvironment.data.key;
	};

	await getOrCreateEnvironment(environment);

	const { data: projects, error: eProjects } = await supabase
		.from('projects')
		.select('*')
		.eq('profile_id', session.user.id);

	if (eProjects || !projects) {
		console.error('Error loading submissions:', eProjects);
		throw error(500, 'Failed to load leads');
	}

	const getOrCreateCritinoProject = async (project: Tables<'projects'>) => {
		console.log('getOrCreateCritinoProject');
		const reletinoEnvironment = await critino.GET('/environments/{name}', {
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
		console.log('reletinoEnvironment', reletinoEnvironment);

		if (reletinoEnvironment.error) {
			console.log('getOrCreateCritinoProject error');
			const createProject = await critino.POST('/environments/{name}', {
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

			if (!createProject.data?.key || createProject.error) {
				console.error('Error creating project:', createProject.error);
				throw error(500, 'Failed to create project');
			}

			environment.critino_key = createProject.data?.key;
			console.log('createProject', createProject);
		}
	};

	for (const project of projects) {
		await getOrCreateCritinoProject(project);
	}

	return {
		projects,
		usage,
	};
};
