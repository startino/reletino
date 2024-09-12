import { supabase } from '$lib/supabase';

import type { Actions, PageServerLoad } from './$types';

import type { Lead } from '$lib/types/';

import { fetchPostAndEvaluate } from '$lib/server/controllers/evaluation';


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
	  markAsDone: async ({request, url}) => {
		const {id} = await request.json()
		console.log('markAsDone', id);

		if (!id) {
			console.error('Error: no id provided')
			return {
				success: false,
			}
		}
		const {data, error} = await supabase.from('leads').update({done: true}).eq('id', id);

		if (error || !data) {
			console.error('Error: ', error || 'No data returned (!data)');
			return {
				success: true,
			}
		}

		console.log('markAsDone', id);
		
		return {
		  success: true
		};
	  }




	// markAsDone: async ({request}) => {
	// 	const formData = await request.formData();
	// 	const id: string = formData.get('id') as string;

	// 	if (!id) {
	// 				console.error('Error: no id provided')
	// 				return {
	// 					success: false,
	// 				}
	// 				}
	// 	const {data, error} = await supabase.from('leads').update({done: true}).eq('id', id);

	// 	if (error || !data) {
	// 		console.error('Error: ', error || 'No data returned (!data)');
	// 		return {
	// 			success: false,
	// 		}
	// 	}
	// 	console.log('markAsDone', id);
	// 	return {
	// 	  success: true
	// 	};
	//   },
};
