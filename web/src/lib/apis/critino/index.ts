import createClient from 'openapi-fetch';
import type { paths, components } from './v0.d.ts';
import { PUBLIC_CRITINO_API_KEY, PUBLIC_CRITINO_API_URL, PUBLIC_OPENROUTER_API_KEY } from '$env/static/public';
import { getURL } from '$lib/utils';
import type { Tables } from '$lib/supabase';

const api = createClient<paths>({ baseUrl: getURL(PUBLIC_CRITINO_API_URL) });

type schemas = components['schemas'];
type headers = components['headers'];
type responses = components['responses'];
type parameters = components['parameters'];
type requestBodies = components['requestBodies'];
type pathItems = components['pathItems'];

export type { paths, schemas, headers, responses, parameters, requestBodies, pathItems };

export const handleSubmissionCritique = async ({
    submission,
    projectName,
    teamName,
    response,
    optimal,
}: {
    submission: Tables<'submissions'>,
    projectName: string,
    teamName: string,
    response: string | undefined,
    optimal: {reasoning: string, isRelevant: boolean},
}) => {
    const query = `<title>${submission.title}</title><selftext>${submission.selftext}</selftext>`;

    const postObject = {
        params: {
            path: { id: submission.id },
            query: {
                team_name: 'startino', // Critino team is different from a team on Reletino.
                environment_name: 'reletino/' + teamName + '/' + projectName + '/evaluator',
                populate_missing: true,
                similarity_key: 'query' as const,
            },
            header: {
                'x-critino-key': PUBLIC_CRITINO_API_KEY,
                'x-openrouter-api-key': PUBLIC_OPENROUTER_API_KEY
            },
        },
        body: {
            context: "",
            query,
            optimal: JSON.stringify(optimal),
            response,
            instructions: "",
        },
    };
    console.log(`Creating Critique with object: ${JSON.stringify(postObject, null, 2)}...`);

    const res = await api.POST('/critiques/{id}', postObject);
    console.log(`Creating Critique with response: ${JSON.stringify(res, null, 2)}`);

    if (!res.data || res.error) {
        console.error(`Error creating critique: ${JSON.stringify(res.error, null, 2)}`);
        return null;
    }

    return res.data;
};

// Critique the DM/comment that the AI generated
export const handleCommentOrDmCritique = async ({
    submission,
    response,
    optimal,
    projectName,
    teamName,
    isDm,
}: {
    submission: Tables<'submissions'>,
    response: string,
    optimal: string,
    projectName: string,
    teamName: string,
    isDm: boolean,
}) => {
    // Give the submission as context
    const query = `<title>${submission.title}</title><selftext>${submission.selftext}</selftext>`;

    const postObject = {
        params: {
            path: { id: submission.id },
            query: {
                team_name: 'startino',
                environment_name: 'reletino/' + teamName + '/' + projectName + (isDm ? '/dm-generator' : '/comment-generator'),
                populate_missing: true,
                similarity_key: 'situation' as const,
            },
            header: {
                'x-critino-key': PUBLIC_CRITINO_API_KEY,
                'x-openrouter-api-key': PUBLIC_OPENROUTER_API_KEY
            },
        },
        body: {
            context: "",
            query,
            optimal,
            response,
            instructions: "",
        },
    };
    
    const res = await api.POST('/critiques/{id}', postObject);
    console.log(`Creating Critique with response: ${JSON.stringify(res, null, 2)}`);

    if (!res.data || res.error) {
        console.error(`Error creating critique: ${JSON.stringify(res.error, null, 2)}`);
        return null;
    }
};

export default api;
