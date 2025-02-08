import { redirect } from '@sveltejs/kit';
import { message, superValidate } from 'sveltekit-superforms';
import { zod } from 'sveltekit-superforms/adapters';
import { z } from 'zod';
import { PRIVATE_API_URL } from '$env/static/private';

const profileResearchSchema = z.object({
    username: z.string().min(1, 'Username is required'),
});

export const load = async ({ locals: { safeGetSession } }) => {
    const { session } = await safeGetSession();

    if (!session) {
        redirect(303, '/login');
    }

    return {
        form: await superValidate(zod(profileResearchSchema)),
    };
};

export const actions = {
    analyze: async ({ request, fetch }) => {
        const form = await superValidate(request, zod(profileResearchSchema));

        if (!form.valid) {
            return message(form, {
                type: 'error',
                text: 'Please provide a valid username',
            });
        }

        try {
            const response = await fetch(`${PRIVATE_API_URL}/analyze-profile`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    username: form.data.username,
                }),
            });

            const data = await response.json();

            if (!response.ok) {
                console.error('API Error:', data);
                return message(form, {
                    type: 'error',
                    text: data.detail || 'Failed to analyze profile',
                });
            }

            if (!data.analysis) {
                return message(form, {
                    type: 'error',
                    text: 'No analysis data returned',
                });
            }

            return {
                form,
                analysis: data.analysis,
            };
        } catch (error) {
            console.error('Error analyzing profile:', error);
            return message(form, {
                type: 'error',
                text: 'Failed to connect to analysis service. Please try again.',
            });
        }
    },
}; 