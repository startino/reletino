import { supabase } from '$lib/supabase';
import { error, fail } from '@sveltejs/kit';
import type { Actions, PageServerLoad } from './$types';
import { superValidate } from 'sveltekit-superforms/server';
import type { Database, Tables, Enums } from '$lib/types/supabase';
import type { Lead } from '$lib/types/';
import { markAsDone } from '$lib/api.js';

export const load = async ({ locals }) => {
	const session = await locals.getSession();

	const { data, error } = await supabase.from('leads').select('*');

	let leads = data as Lead[];
	return { leads };
};
export const actions: Actions = {
	done: async ({ params, locals }) => {
		const leadId = params.id as string;
		const data = supabase.from('leads').update({status: 'subscriber'}).eq('id', leadId);
		if (!data) {
			throw error(500, 'Failed attempt at updating lead');
		}
	}
};
