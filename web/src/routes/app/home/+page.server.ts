import { supabase } from '$lib/supabase';
import { error, fail } from '@sveltejs/kit';
import type { Actions, PageServerLoad } from './$types';
import { superValidate } from 'sveltekit-superforms/server';
import type { Database, Tables, Enums } from '$lib/types/supabase';
import type { Lead } from '$lib/types/';
import { markAsDone } from '$lib/api.js';
import { fetchPostAndEvaluate } from '$lib/server/controllers/evaluation';
import { generateDM } from '$lib/server/ai/agent/dmGenerator.js';

export const load = async ({ locals }) => {
	const session = await locals.getSession();

	const { data, error } = await supabase.from('leads').select('*');

	let leads = data as Lead[];
	return { leads };
};
export const actions: Actions = {
	fetchPostAndEvaluate: async ({ params, locals }) => {
		await fetchPostAndEvaluate();
	  },
	generateDM: async ({ params, locals }) => {
		const { post } = params.post;
		const message = await generateDM(post);
		return { message };
	},
	markAsDone: async ({ params, locals, url }) => {
		const id: string | null = params.id;
		console.log("Marking as done: " + JSON.stringify(params), JSON.stringify(locals), JSON.stringify(url));
		if (!id) {
			return 'No id provided';
		}
		

		const { data, error } = supabase.from('leads').update({ done: true }).eq('id', id);
		if (error || !data) {
			return "Error: " + error;
		}
		return "Success";
	},
};
