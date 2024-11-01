import { redirect } from '@sveltejs/kit';

export const load = async ({ locals: { environment, auth } }) => {
	redirect(303, `/dashboard/${environment?.name}/projects`);
};
