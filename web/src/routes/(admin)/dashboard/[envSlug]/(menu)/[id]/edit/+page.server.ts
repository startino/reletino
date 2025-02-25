import { projectSchema } from '$lib/schemas';
import { redirect } from '@sveltejs/kit';
import { message, superValidate } from 'sveltekit-superforms';
import { zod } from 'sveltekit-superforms/adapters';
import { PRIVATE_API_URL } from '$env/static/private';

export const load = async ({ locals: { safeGetSession } }) => {
	const { session } = await safeGetSession();

	if (!session) {
		redirect(303, '/login');
	}

	return {
		projectForm: await superValidate(zod(projectSchema)),
	};
};

export const actions = {
	updateProject: async ({ request, params, locals: { supabase } }) => {
		let formData;
		const contentType = request.headers.get('content-type');

		if (contentType === 'application/json') {
			formData = await request.json();
			// Create a form object compatible with superValidate
			const form = await superValidate(formData, zod(projectSchema));
			if (!form.valid) {
				return { type: 'error', text: 'Error occurred when saving project.' };
			}
			formData = form;
		} else {
			formData = await superValidate(request, zod(projectSchema));
			if (!formData.valid) {
				return message(formData, {
					type: 'error',
					text: 'Error occurred when saving project.',
				});
			}
		}

		const { data: env, error: eEnv } = await supabase
			.from('environments')
			.select('name')
			.eq('slug', params.envSlug)
			.single();

		if (!env || eEnv) {
			return contentType === 'application/json' 
				? { type: 'error', text: 'Could not save project from an error with finding env name.' }
				: message(formData, {
					type: 'error',
					text: 'Could not save project from an error with finding env name.',
				});
		}

		// First save the project to the database
		const { data, error, status } = await supabase
			.from('projects')
			.upsert({
				...formData.data,
			})
			.select();

		if (error || !data) {
			return contentType === 'application/json'
				? { type: 'error', text: 'Error occurred when saving project.' }
				: message(formData, {
					type: 'error',
					text: 'Error occurred when saving project.',
				});
		}

		// Trigger backend operation asynchronously
		if (formData.data.running) {
			// Start the project asynchronously
			fetch(`${PRIVATE_API_URL}/start`, {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
				},
				body: JSON.stringify({
					project: {
						id: formData.data.id,
						title: formData.data.title,
						profile_id: formData.data.profile_id,
						prompt: formData.data.prompt,
						subreddits: formData.data.subreddits,
						running: formData.data.running,
					},
					team_name: env.name,
				}),
			}).catch(error => {
				console.error('Error starting project:', error);
			});
		} else {
			// Stop the project asynchronously
			fetch(`${PRIVATE_API_URL}/stop`, {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
				},
				body: JSON.stringify({
					project_id: formData.data.id,
				}),
			}).catch(error => {
				console.error('Error stopping project:', error);
			});
		}

		if (status == 201) {
			return contentType === 'application/json'
				? { type: 'success', text: 'Project Created!' }
				: message(formData, { type: 'success', text: 'Project Created!' });
		} else {
			return contentType === 'application/json'
				? { type: 'success', text: 'Project Updated!' }
				: message(formData, { type: 'success', text: 'Project Updated!' });
		}
	},
};
