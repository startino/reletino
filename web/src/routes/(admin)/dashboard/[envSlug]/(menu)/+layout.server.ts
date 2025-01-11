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

	console.log("PUBLIC_CRITINO_API_KEY", PUBLIC_CRITINO_API_KEY);

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

	const getOrCreateTeamEnv = async () => {
		if (environment.critino_key) {
		  console.log('environment key already exists');
		  return;
		}
		console.log('environment', environment);

		// Reletino hiearchy:
		// environment (team) -> environment_profile (relationship) -> profile (user) -> project
		// but environment 1:1 with profile 
	  
		const critinoTeamEnv = await critino.GET('/environments/{name}', {
		  params: {
			query: {
			  team_name: 'startino',
			  parent_name: 'reletino'
			},
			path: {
			  name: environment.name
			},
			header: {
			  'x-critino-key': PUBLIC_CRITINO_API_KEY,
			},
		  },
		});

		console.log('reletinoEnvironment', environment);
	  
		if (!critinoTeamEnv.error) {
		  const updateKeyResponse = await critino.PATCH('/environments/{name}/key', {
			params: {
			  query: {
				team_name: 'startino',
				parent_name: 'reletino'
			  },
			  path: {
				name: environment.name
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
			.eq('name', environment.name);
	  
		  console.log('error env', environment.name, eEnvironment);
		  environment.critino_key = updateKeyResponse.data.key;

		  return;
		}

		console.log('create new critino team env');
	  
		const newCritinoTeamEnv = await critino.POST('/environments/{name}', {
			params: {
				query: {
					team_name: 'startino',
					parent_name: 'reletino',
				},
				path: {
					name: environment.name,
				},
				header: {
					'x-critino-key': PUBLIC_CRITINO_API_KEY,
				},
			},
			body: {
				description: `env name: ${environment.name}\nemail: ${auth.user?.email}\nuser id: ${auth.user?.id}`,
				gen_key: false
			},
		});

		console.log('newCritinoEnv', newCritinoTeamEnv);

		if (!newCritinoTeamEnv.data || newCritinoTeamEnv.error) {
			console.error(
				`Error creating environment: ${JSON.stringify(newCritinoTeamEnv.error, null, 2)}`
			);
			throw error(500, 'Failed to update environment key');
		}

		const { error: eTeamEnv } = await supabase
			.from('environments')
			.update({ critino_key: newCritinoTeamEnv.data.key })
			.eq('name', environment.name);

		if (eTeamEnv) {
			console.error(`Error updating environment: ${JSON.stringify(eTeamEnv, null, 2)}`);
			throw error(500, 'Failed to update environment');
		}

		environment.critino_key = newCritinoTeamEnv.data.key;
	};

	console.log('environment', environment);
	await getOrCreateTeamEnv();

	const { data: projects, error: eProjects } = await supabase
		.from('projects')
		.select('*')
		.eq('profile_id', session.user.id);

	if (eProjects || !projects) {
		console.error('Error loading submissions:', eProjects);
		throw error(500, 'Failed to load leads');
	}

	const getOrCreateCritinoProjectEnv = async (project: Tables<'projects'>) => {
		console.log('getOrCreateCritinoProject');
		const critinoProjectEnv = await critino.GET('/environments/{name}', {
			params: {
				query: {
					team_name: 'startino',
					parent_name: 'reletino/' + environment?.name, // TODO: rename environment to teamEnv
				},
				path: {
					name: project.title, // TODO: rename project title to project name
				},
				header: {
					'x-critino-key': PUBLIC_CRITINO_API_KEY,
				},
			},
		});
		console.log('critinoProjectEnv', critinoProjectEnv);

		if (critinoProjectEnv.error) {
			console.log('getOrCreateCritinoProject error');
			const createCritinoProjectEnv = await critino.POST('/environments/{name}', {
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
					description: `project name: ${project.title}\nemail: ${auth.user?.email}\nuser id: ${auth.user?.id}`, // TODO: rename project title to project name
				},
			});

			if (!createCritinoProjectEnv.data?.key || createCritinoProjectEnv.error) {
				console.error('Error creating project:', createCritinoProjectEnv.error);
				throw error(500, 'Failed to create project');
			}

			environment.critino_key = createCritinoProjectEnv.data?.key;
			console.log('createCritinoProjectEnv', createCritinoProjectEnv);
		}
	};

	for (const project of projects) {
		getOrCreateCritinoProjectEnv(project).catch((e) => {
			throw e;
		});
	}

	return {
		projects,
		usage,	
	};
};
