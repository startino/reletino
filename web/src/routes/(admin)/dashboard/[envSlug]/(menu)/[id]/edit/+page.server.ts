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

		// Used for telling the user if the server was able to start/stop the project
		let responseStatus: 'success' | 'error' = 'error';

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

		if (formData.data.running) {
			// Start the project
			await fetch(`${PRIVATE_API_URL}/start`, {
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
					project_id: formData.data.id,
				}),
			})
				.then((res) => res.json())
				.then((data) => (responseStatus = data.status));
		}

		if (responseStatus == 'error') {
			return contentType === 'application/json'
				? { type: 'error', text: "Our server couldn't fulfill your request. Try again or contact me: jorge.lewis@starti.no" }
				: message(formData, {
					type: 'error',
					text: "Our server couldn't fulfill your request. Try again or contact me: jorge.lewis@starti.no",
				});
		}

		const { data, error, status } = await supabase
			.from('projects')
			.upsert({
				...formData.data,
			})
			.select();

		if (status == 201) {
			return contentType === 'application/json'
				? { type: 'success', text: 'Project Created!' }
				: message(formData, { type: 'success', text: 'Project Created!' });
		} else if (status == 200) {
			return contentType === 'application/json'
				? { type: 'success', text: 'Project Updated!' }
				: message(formData, { type: 'success', text: 'Project Updated!' });
		}

		if (error || !data) {
			return contentType === 'application/json'
				? { type: 'error', text: 'Error occurred when saving project.' }
				: message(formData, {
					type: 'error',
					text: 'Error occurred when saving project.',
				});
		}

		return contentType === 'application/json'
			? { type: 'success', text: 'Project Updated!' }
			: message(formData, { type: 'success', text: 'Project Updated!' });
	},
};
