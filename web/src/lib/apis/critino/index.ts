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

export const handleCritique = async (
    submission: Tables<'submissions'>, 
    projectName: string, 
    environmentName: string,
    context: string = '',
) => {
    const query = `<title>${submission.title}</title><selftext>${submission.selftext}</selftext>`;
    const response = `{"reasoning": "${submission.reasoning}", "is_relevant": "${submission.is_relevant}"}`;
    const optimal = '';

    const postObject = {
        params: {
            path: { id: submission.id },
            query: {
                team_name: 'startino',
                environment_name: 'reletino/' + environmentName + '/' + projectName,
                populate_missing: true,
                similarity_key: 'situation' as const,
            },
            header: {
                'x-critino-key': PUBLIC_CRITINO_API_KEY,
                'x-openrouter-api-key': PUBLIC_OPENROUTER_API_KEY
            },
        },
        body: {
            context,
            query,
            optimal,
            response,
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

export const getOrCreateEnvironment = async (environmentName: string, description: string) => {
    console.log('environment key does not exist');

    const readResponse = await api.GET('/environments/{name}', {
        params: {
            query: {
                team_name: 'startino',
                parent_name: 'reletino',
            },
            path: {
                name: environmentName,
            },
            header: {
                'x-critino-key': PUBLIC_CRITINO_API_KEY,
            },
        },
    });
    console.log('readResponse', readResponse);

    // update key if it exists but we don't have the key
    if (!readResponse.error) {
        const updateKeyResponse = await api.PATCH('/environments/{name}/key', {
            params: {
                path: {
                    name: environmentName,
                },
                query: {
                    team_name: 'startino',
                    parent_name: 'reletino',
                },
                header: {
                    'x-critino-key': PUBLIC_CRITINO_API_KEY,
                },
            },
        });
        console.log('updateKeyResponse', updateKeyResponse);

        if (!updateKeyResponse.data || updateKeyResponse.error) {
            console.error(
                `Error updating environment key: ${JSON.stringify(updateKeyResponse.error, null, 2)}`
            );
            return null;
        }

        return updateKeyResponse.data.key;
    }

    const createResponse = await api.POST('/environments/{name}', {
        params: {
            query: {
                team_name: 'startino',
                parent_name: 'reletino',
            },
            path: {
                name: environmentName,
            },
            header: {
                'x-critino-key': PUBLIC_CRITINO_API_KEY,
            },
        },
        body: {
            gen_key: true,
            description,
        },
    });
    console.log('createResponse', createResponse);

    if (!createResponse.data || createResponse.error) {
        console.error(
            `Error creating environment: ${JSON.stringify(createResponse.error, null, 2)}`
        );
        return null;
    }

    return createResponse.data.key;
};

export const getOrCreateProject = async (projectName: string, environmentName: string, description: string) => {
    console.log('getOrCreateCritinoProject');
    const readResponse = await api.GET('/environments/{name}', {
        params: {
            query: {
                team_name: 'startino',
                parent_name: 'reletino/' + environmentName,
            },
            path: {
                name: projectName,
            },
            header: {
                'x-critino-key': PUBLIC_CRITINO_API_KEY,
            },
        },
    });
    console.log('readResponse', readResponse);

    if (readResponse.error) {
        console.log('getOrCreateCritinoProject error');
        const createResponse = await api.POST('/environments/{name}', {
            params: {
                query: {
                    team_name: 'startino',
                    parent_name: 'reletino/' + environmentName,
                },
                path: {
                    name: projectName,
                },
                header: {
                    'x-critino-key': PUBLIC_CRITINO_API_KEY,
                },
            },
            body: {
                gen_key: false,
                description,
            },
        });

        if (!createResponse.data || createResponse.error) {
            console.error(`Error creating project: ${JSON.stringify(createResponse.error, null, 2)}`);
            return null;
        }

        return createResponse.data.key;
    }

    return null;
};

export default api;
