import { superValidate } from 'sveltekit-superforms/server';
import { zod } from 'sveltekit-superforms/adapters';
import { projectFormSchema } from '$lib/schemas';
import type { Actions } from './$types';
import { fail } from '@sveltejs/kit';

export const load = async () => {
	const form = await superValidate(zod(projectFormSchema));
	return { form };
};

export const actions: Actions = {
	default: async ({ request }) => {
		const form = await superValidate(request, zod(projectFormSchema));

		if (!form.valid) {
			console.log(form.errors);
			return fail(400, { form });
		}

		// Handle the form submission here
		console.log(form.data);

		return { form };
	},
};
