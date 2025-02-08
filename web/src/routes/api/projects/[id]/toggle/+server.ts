import { json } from '@sveltejs/kit';
import { PRIVATE_API_URL } from '$env/static/private';
import { projectSchema } from '$lib/schemas';
import { superValidate } from 'sveltekit-superforms';
import { zod } from 'sveltekit-superforms/adapters';

export async function POST({ request, params, locals: { supabase } }) {
	try {
		const projectId = params.id;
		const rawData = await request.json();
		const { environment_slug, ...projectData } = rawData;

		// Validate the project data
		const form = await superValidate(projectData, zod(projectSchema));
		if (!form.valid) {
			return json(
				{ type: 'error', text: 'Error occurred when validating project data.' },
				{ status: 400 }
			);
		}

		// Get environment info
		const { data: env, error: eEnv } = await supabase
			.from('environments')
			.select('name, slug')
			.eq('slug', environment_slug)
			.single();

		if (!env || eEnv) {
			return json(
				{ type: 'error', text: 'Could not find environment.' },
				{ status: 404 }
			);
		}

		// Used for telling the user if the server was able to start/stop the project
		let responseStatus: 'success' | 'error' = 'error';

		if (form.data.running) {
			// Start the project
			await fetch(`${PRIVATE_API_URL}/start`, {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
				},
				body: JSON.stringify({
					project: {
						id: form.data.id,
						title: form.data.title,
						profile_id: form.data.profile_id,
						prompt: form.data.prompt,
						subreddits: form.data.subreddits,
						running: form.data.running,
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
					project_id: projectId,
				}),
			})
				.then((res) => res.json())
				.then((data) => (responseStatus = data.status));
		}

		if (responseStatus === 'error') {
			return json(
				{
					type: 'error',
					text: "Our server couldn't fulfill your request. Try again or contact me: jorge.lewis@starti.no",
				},
				{ status: 500 }
			);
		}

		// Update project in database
		const { data, error, status } = await supabase
			.from('projects')
			.upsert({
				...form.data,
			})
			.select();

		if (error || !data) {
			return json(
				{ type: 'error', text: 'Error occurred when saving project.' },
				{ status: 500 }
			);
		}

		return json({
			type: 'success',
			text: `Project ${form.data.running ? 'started' : 'stopped'} successfully!`,
		});
	} catch (error) {
		console.error('Error processing request:', error);
		return json(
			{ type: 'error', text: 'An unexpected error occurred.' },
			{ status: 500 }
		);
	}
} 