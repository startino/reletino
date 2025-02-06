import { superValidate, fail, setError } from 'sveltekit-superforms';
import { zod } from 'sveltekit-superforms/adapters';
import { projectFormSchema } from '$lib/schemas';
import { redirect } from '@sveltejs/kit';

export const load = async () => {
	const form = await superValidate(zod(projectFormSchema));
	return { form };
};

export const actions = {
	default: async ({ request, locals: { supabase, safeGetSession, environment } }) => {
		const form = await superValidate(request, zod(projectFormSchema));

		if (!form.valid) {
			console.log(form.errors);
			return fail(400, { form });
		}

		const session = await safeGetSession();

		const { projectName, websiteUrl, category, context } = form.data;

		const { data, error } = await supabase
			.from('projects')
			.insert({
				profile_id: session.user!.id,
				title: projectName,
				category,
				context,
				website_url: websiteUrl,
				running: true,
			})
			.select()
			.single();

		if (error) {
			console.error(error);
			return setError(form, 'Something went wrong', { status: 500 });
		}

		redirect(302, `/dashboard/${environment!.slug}/projects/${data.id}/edit`);
	},
};
