import { projectSchema } from '$lib/schemas';
import { redirect } from '@sveltejs/kit';
import { message, superValidate } from 'sveltekit-superforms';
import { zod } from 'sveltekit-superforms/adapters';
import type { Tables } from '$lib/supabase';
import { PRIVATE_API_URL } from '$env/static/private';

export const load = async ({ locals: { safeGetSession, supabase } }) => {
	const { session } = await safeGetSession();

	if (!session) {
		redirect(303, '/login');
	}

	const { data, error } = await supabase
		.from('projects')
		.select('*')
		.eq('profile_id', session.user.id);

	if (error || !data) {
		console.error('Error loading submissions:', error);
		return { status: 500, error: new Error('Failed to load leads') };
	}

	const projects = data as Tables<'projects'>[];

	return {
		projectForm: await superValidate(zod(projectSchema)),
		projects,
	};
};

export const actions = {
	updateProject: async ({ request, params, locals: { supabase } }) => {
		const form = await superValidate(request, zod(projectSchema));

		if (!form.valid) {
			return message(form, {
				type: 'error',
				text: 'Error occured when saving project.',
			});
		}

		// Used for telling the user if the server was able to start/stop the project
		let responseStatus: 'success' | 'error' = 'error';

		const { data: env, error: eEnv } = await supabase
			.from('environments')
			.select('name')
			.eq('slug', params.envSlug)
			.single();

		if (!env || eEnv) {
			return message(form, {
				type: 'error',
				text: 'Could not save project from an error with finding env name.',
			});
		}

		if (form.data.running) {
			// Start the project
			await fetch(`${PRIVATE_API_URL}/start`, {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
				},
				body: JSON.stringify({
					project: { ...form.data },
					environment_name: env.name,
				}),
			})
				.then((res) => res.json())
				.then((data) => (responseStatus = data.status));
		} else {
			// Stop the project
			await fetch(`${PRIVATE_API_URL}/stop`, {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
				},
				body: JSON.stringify({
					project_id: form.data.id,
				}),
			})
				.then((res) => res.json())
				.then((data) => (responseStatus = data.status));
		}

		if (responseStatus == 'error') {
			return message(form, {
				type: 'error',
				text: "Our server couldn't fulfill your request. Try again or contact me: jorge.lewis@starti.no",
			});
		}

		const { data, error, status } = await supabase
			.from('projects')
			.upsert({
				...form.data,
			})
			.select();

		if (status == 201) {
			return message(form, { type: 'success', text: 'Project Created!' });
		} else if (status == 200) {
			return message(form, { type: 'success', text: 'Project Updated!' });
		}

		if (error || !data) {
			return message(form, {
				type: 'error',
				text: 'Error occured when saving project.',
			});
		}

		return message(form, { type: 'success', text: 'Project Updated!' });
	},
};
