<script lang="ts">
	import { Button } from '$lib/components/ui/button';
	import * as Dialog from '$lib/components/ui/dialog';
	import * as Form from '$lib/components/ui/form';
	import * as Select from '$lib/components/ui/select';
	import { Input } from '$lib/components/ui/input';
	import { Textarea } from '$lib/components/ui/textarea';
	import { projectSchema, type ProjectSchema } from '$lib/schemas';
	import { LoaderCircle, Loader, ExternalLink } from 'lucide-svelte';
	import type { Tables } from '$lib/supabase';
	import {
		superForm,
		type SuperForm,
		type SuperValidated,
		type Infer,
	} from 'sveltekit-superforms';
	import { zodClient } from 'sveltekit-superforms/adapters';
	import { X } from 'lucide-svelte';
	import { Typography } from '$lib/components/ui/typography';
	import { toast } from 'svelte-sonner';
	import type { SupabaseClient, Session } from '@supabase/supabase-js';
	import { Switch } from '$lib/components/ui/switch';
	import { Root } from '$lib/components/ui/accordion';
	import { PUBLIC_CRITINO_URL } from '$env/static/public';
	import { TipTap } from '$lib/components/ui/tiptap';
	import { generateHTML } from '@tiptap/core';
	import StarterKit from '@tiptap/starter-kit';

	interface Props {
		session: Session;
		supabase: SupabaseClient<any, 'public', any>;
		projectForm: SuperValidated<Infer<ProjectSchema>>;
		environment: Tables<'environments'>;
		selectedProjectId: string;
		newProject: Tables<'projects'> | null;
		projects: Tables<'projects'>[];
	}

	let {
		session,
		supabase,
		environment,
		projectForm,
		selectedProjectId = $bindable(),
		projects = $bindable(),
		newProject = $bindable(),
	}: Props = $props();

	let selectedProject: Tables<'projects'> =
		newProject ?? projects.find((project) => project.id == selectedProjectId)!;

	const form = superForm(projectForm, {
		delayMs: 400,
		timeoutMs: 3000,
		onSubmit: async () => {},
		validators: zodClient(projectSchema),
		resetForm: false,
		onResult: ({ result, formElement, cancel }) => {
			if (result.type == 'success') {
				if (!projects.some((project) => project.id === $formData.id)) {
					projects.push($formData as Tables<'projects'>);
				} else {
					projects = projects.map((project) =>
						project.id === $formData.id ? ($formData as Tables<'projects'>) : project
					);
				}
			}
		},
		onUpdated({ form }) {
			newProject = null;
			if (form.message) {
				if (form.message.type == 'error') {
					toast.error(form.message.text);
				} else if (form.message.type == 'success') {
					toast.success(form.message.text);
				}
			}
		},
	});

	const { form: formData, errors, enhance, message, delayed, timeout } = form;

	$effect(() => {
		$formData = selectedProject;
	});

	let subreddits: { label: string; value: string }[] = $derived(
		$formData.subreddits.map((subreddit) => ({
			label: subreddit,
			value: subreddit,
		}))
	);

	let newSubreddit: string = $state('');

	const addSubreddit = () => {
		if (newSubreddit != '') {
			newSubreddit = newSubreddit.toLowerCase().trim().replace('r/', '');
			$formData.subreddits = [...$formData.subreddits, newSubreddit];
		}
		newSubreddit = '';
	};

	const deleteProject = async () => {
		const { data, error } = await supabase
			.from('projects')
			.delete()
			.eq('id', selectedProjectId)
			.select();
		if (error) {
			toast.error('An error occurred. Try again.');
		} else if (!data) {
			console.log(data);
			toast.error('Could not delete project. Project not found.');
		} else {
			projects = projects.filter((project) => project.id != selectedProjectId);
			selectedProjectId = '';
			toast.success('Project successfully deleted.');
		}
	};

	const fillPromptWithTemplate = () => {
		const defaultPrompt = generateHTML(
			{
				type: 'doc',
				content: [
					{
						type: 'heading',
						attrs: { level: 1 },
						content: [{ type: 'text', text: 'Objective' }],
					},
					{
						type: 'paragraph',
						content: [
							{
								type: 'text',
								text: 'The end-goal is to use the relevant posts to acquire new users for Reletino.',
							},
						],
					},
					{
						type: 'heading',
						attrs: { level: 1 },
						content: [{ type: 'text', text: 'General Guidance' }],
					},
					{
						type: 'paragraph',
						content: [
							{
								type: 'text',
								text: 'The author must own/run an existing SaaS product or is planning on building one.',
							},
						],
					},
					{
						type: 'heading',
						attrs: { level: 1 },
						content: [{ type: 'text', text: 'Relevant Post Examples' }],
					},
					{
						type: 'paragraph',
						content: [
							{
								type: 'text',
								text: 'A post of someone asking for marketing tools they can use to help sell their software product.',
							},
						],
					},
					{
						type: 'paragraph',
						content: [
							{
								type: 'text',
								text: 'A post from someone that is running a SaaS business and needs to market it.',
							},
						],
					},
					{
						type: 'heading',
						attrs: { level: 1 },
						content: [{ type: 'text', text: 'Irrelevant Post Examples' }],
					},
					{
						type: 'bulletList',
						content: [
							{
								type: 'listItem',
								content: [
									{
										type: 'paragraph',
										content: [
											{
												type: 'text',
												text: "A really technical post about a person's software.",
											},
										],
									},
								],
							},
							{
								type: 'listItem',
								content: [
									{
										type: 'paragraph',
										content: [
											{
												type: 'text',
												text: 'Someone with an idea that is too vague or still in the concept phase, with the author not already committing to building the product.',
											},
										],
									},
								],
							},
							{
								type: 'listItem',
								content: [
									{
										type: 'paragraph',
										content: [
											{
												type: 'text',
												text: 'A post related to e-commerce or physical products.',
											},
										],
									},
								],
							},
						],
					},
					{
						type: 'heading',
						attrs: { level: 1 },
						content: [{ type: 'text', text: 'About Reletino' }],
					},
					{
						type: 'paragraph',
						content: [{ type: 'text', text: 'Reletino is a Reddit automation tool.' }],
					},
					{
						type: 'paragraph',
						content: [
							{
								type: 'text',
								text: 'Its primary goal is to help users find relevant posts.',
							},
						],
					},
					{
						type: 'paragraph',
						content: [
							{
								type: 'text',
								text: "It uses AI to filter a live stream of Reddit posts based on a prompt; you simply tell it what is relevant to you in plain English and it'll give you relevant posts as they get published.",
							},
						],
					},
					{
						type: 'paragraph',
						content: [
							{
								type: 'text',
								text: 'Reletino is great at connecting someone with a product/service to someone that needs it.',
							},
						],
					},
					{
						type: 'paragraph',
						content: [
							{
								type: 'text',
								text: "Reletino is like RedditFlow and GummySearch, but instead of using keywords which don't capture nuance, Reletino does.",
							},
						],
					},
				],
			},
			[StarterKit]
		);
		$formData.filter_prompt = defaultPrompt;
	};

	const fillCommentStyleWithTemplate = () => {
		const defaultCommentStyle = generateHTML(
			{
				type: 'doc',
				content: [
					{
						type: 'heading',
						attrs: { level: 1 },
						content: [{ type: 'text', text: 'Comment Style Guide' }],
					},
					{
						type: 'paragraph',
						content: [
							{
								type: 'text',
								text: 'Be friendly and professional when commenting on posts.',
							},
						],
					},
					{
						type: 'bulletList',
						content: [
							{
								type: 'listItem',
								content: [
									{
										type: 'paragraph',
										content: [
											{
												type: 'text',
												text: 'Always start with a greeting.',
											},
										],
									},
								],
							},
							{
								type: 'listItem',
								content: [
									{
										type: 'paragraph',
										content: [
											{
												type: 'text',
												text: 'Acknowledge their specific situation or problem.',
											},
										],
									},
								],
							},
							{
								type: 'listItem',
								content: [
									{
										type: 'paragraph',
										content: [
											{
												type: 'text',
												text: 'Explain how our product can help them.',
											},
										],
									},
								],
							},
							{
								type: 'listItem',
								content: [
									{
										type: 'paragraph',
										content: [
											{
												type: 'text',
												text: 'End with a clear call to action.',
											},
										],
									},
								],
							},
						],
					},
				],
			},
			[StarterKit]
		);
		$formData.comment_style_prompt = defaultCommentStyle;
	};

	const fillDMStyleWithTemplate = () => {
		const defaultDMStyle = generateHTML(
			{
				type: 'doc',
				content: [
					{
						type: 'heading',
						attrs: { level: 1 },
						content: [{ type: 'text', text: 'DM Style Guide' }],
					},
					{
						type: 'paragraph',
						content: [
							{
								type: 'text',
								text: 'Be concise and professional when sending direct messages.',
							},
						],
					},
					{
						type: 'bulletList',
						content: [
							{
								type: 'listItem',
								content: [
									{
										type: 'paragraph',
										content: [
											{
												type: 'text',
												text: 'Introduce yourself and your role.',
											},
										],
									},
								],
							},
							{
								type: 'listItem',
								content: [
									{
										type: 'paragraph',
										content: [
											{
												type: 'text',
												text: 'Reference their specific post or comment.',
											},
										],
									},
								],
							},
							{
								type: 'listItem',
								content: [
									{
										type: 'paragraph',
										content: [
											{
												type: 'text',
												text: 'Explain why you think our product would be valuable to them.',
											},
										],
									},
								],
							},
							{
								type: 'listItem',
								content: [
									{
										type: 'paragraph',
										content: [
											{
												type: 'text',
												text: 'Provide a clear next step or call to action.',
											},
										],
									},
								],
							},
						],
					},
				],
			},
			[StarterKit]
		);
		$formData.dm_style_prompt = defaultDMStyle;
	};
</script>

<form method="POST" action="?/updateProject" class="flex flex-col gap-y-4" use:enhance>
	<input type="hidden" name="id" bind:value={$formData.id} />
	<input type="hidden" name="profile_id" bind:value={$formData.profile_id} />
	<!-- this button has to be here for disabling submit on enter when focusing on input fields-->
	<!-- https://github.com/sveltejs/kit/discussions/8657 -->
	<button type="submit" disabled style="display: none" />

	<Form.Field {form} name="title">
		<Form.Control let:attrs>
			<Form.Label>Title</Form.Label>
			<Form.Description>This is the project's title.</Form.Description>
			<Input {...attrs} class="max-w-sm" bind:value={$formData.title} />
		</Form.Control>

		<Form.FieldErrors />
	</Form.Field>

	<Form.Field {form} name="subreddits" class="flex flex-col pb-0">
		<Form.Control let:attrs>
			<div class="space-y-0.5">
				<Form.Label>Subreddits</Form.Label>
				<Form.Description>
					Manually add your subreddits, For example: "saas", "startups".
					<br />
					The cost of the project is proportional to the size and number of the subreddits
					you add.
				</Form.Description>
			</div>
			<div class="grid grid-cols-4 items-center gap-3 pt-4">
				<Input
					class="max-w-xs"
					placeholder="Type a subreddit here..."
					bind:value={newSubreddit}
					on:keydown={(e) => {
						if (e.key == 'Enter') {
							addSubreddit();
							newSubreddit = '';
						}
					}}
					on:focusout={addSubreddit}
				/>
				{#if $formData.subreddits.length == 0}
					<Typography variant="body-md" class="col-span-3s text-center">
						No subreddits yet.
					</Typography>
				{:else}
					<Select.Root {...attrs} multiple selected={subreddits}>
						{#each $formData.subreddits as subreddits}
							<input name={attrs.name} hidden value={subreddits} />
						{/each}
					</Select.Root>

					{#each $formData.subreddits as _, i}
						<Button
							variant="outline"
							class="bg-card hover:bg-destructive/20 flex w-full flex-row justify-between rounded-md px-2 py-1"
							on:click={() => {
								$formData.subreddits = $formData.subreddits.filter(
									(subreddit) => subreddit != $formData.subreddits[i]
								);
							}}
						>
							<Typography variant="body-md" class="font-semibold">
								{$formData.subreddits[i]}
							</Typography>
							<X class="text-destructive" />
						</Button>
					{/each}
				{/if}
			</div>
		</Form.Control>

		<Form.FieldErrors />
	</Form.Field>
	<Form.Field {form} name="prompt">
		<Form.Control let:attrs>
			<Form.Label>Prompt</Form.Label>
			<Form.Description>
				Accurate results are achieved by providing a great prompt. <br />
				 Tell the AI exactly what to look for.
			</Form.Description>
			<input type="hidden" name="prompt" bind:value={$formData.filter_prompt} />
			<Dialog.Root>
				<Dialog.Trigger>
					<Button variant="secondary" class="">Open Prompt</Button>
				</Dialog.Trigger>
				<Dialog.Content class="h-full min-h-96 w-full max-w-5xl place-items-center px-7">
					<Button onclick={fillPromptWithTemplate} variant="outline" class="right-2 top-2">
						Insert Example Prompt (Reletino's)
					</Button>
					<div class="h-full min-h-96 w-full p-3">
						<TipTap
							class="h-full max-h-[700px] min-h-[500px] w-full overflow-y-scroll p-3"
							bind:content={$formData.filter_prompt}
						/>
					</div>
				</Dialog.Content>
			</Dialog.Root>
			<Form.FieldErrors />
		</Form.Control>
	</Form.Field>
	<Form.Field {form} name="comment_style_prompt">
		<Form.Control let:attrs>
			<Form.Label>Comment Style</Form.Label>
			<Form.Description>
				Define how the AI should style its comments when responding to relevant posts.
			</Form.Description>
			<input type="hidden" name="comment_style_prompt" bind:value={$formData.comment_style_prompt} />
			<Dialog.Root>
				<Dialog.Trigger>
					<Button variant="secondary" class="">Open Comment Style</Button>
				</Dialog.Trigger>
				<Dialog.Content class="h-full min-h-96 w-full max-w-5xl place-items-center px-7">
					<Button onclick={fillCommentStyleWithTemplate} variant="outline" class="right-2 top-2">
						Insert Example Comment Style
					</Button>
					<div class="h-full min-h-96 w-full p-3">
						<TipTap
							class="h-full max-h-[700px] min-h-[500px] w-full overflow-y-scroll p-3"
							bind:content={$formData.comment_style_prompt}
						/>
					</div>
				</Dialog.Content>
			</Dialog.Root>
			<Form.FieldErrors />
		</Form.Control>
	</Form.Field>
	<Form.Field {form} name="dm_style_prompt">
		<Form.Control let:attrs>
			<Form.Label>DM Style</Form.Label>
			<Form.Description>
				Define how the AI should style its direct messages when reaching out to users.
			</Form.Description>
			<input type="hidden" name="dm_style_prompt" bind:value={$formData.dm_style_prompt} />
			<Dialog.Root>
				<Dialog.Trigger>
					<Button variant="secondary" class="">Open DM Style</Button>
				</Dialog.Trigger>
				<Dialog.Content class="h-full min-h-96 w-full max-w-5xl place-items-center px-7">
					<Button onclick={fillDMStyleWithTemplate} variant="outline" class="right-2 top-2">
						Insert Example DM Style
					</Button>
					<div class="h-full min-h-96 w-full p-3">
						<TipTap
							class="h-full max-h-[700px] min-h-[500px] w-full overflow-y-scroll p-3"
							bind:content={$formData.dm_style_prompt}
						/>
					</div>
				</Dialog.Content>
			</Dialog.Root>
			<Form.FieldErrors />
		</Form.Control>
	</Form.Field>
	<Form.Field
		{form}
		name="running"
		class="flex flex-row items-center justify-between rounded-lg border p-4"
	>
		<Form.Control let:attrs>
			<div class="space-y-0.5">
				<Form.Label>Running</Form.Label>
				<Form.Description>Turn on to start listening for Reddit posts.</Form.Description>
			</div>
			<Switch includeInput {...attrs} bind:checked={$formData.running} />
		</Form.Control>
	</Form.Field>
	<Form.Button class="mt-2 " disabled={$timeout || $delayed}>
		{#if $timeout}
			<LoaderCircle class="animate-spin" />
		{:else if $delayed}
			<Loader class="animate-spin" />
		{:else}
			Save
		{/if}
	</Form.Button>
	<Button
		variant="secondary"
		href={`${PUBLIC_CRITINO_URL}/startino/reletino/${environment.name}/${selectedProject.title}/workflows?key=${environment.critino_key}`}
		target="_blank"
		class="w-full"
	>
		Manage Critiques
		<ExternalLink class="ml-2 w-5" />
	</Button>
	{#if !newProject}
		<Dialog.Root>
			<Dialog.Trigger>
				<Button variant="destructive" class="w-full" disabled={$timeout || $delayed}>
					Delete
				</Button>
			</Dialog.Trigger>
			<Dialog.Content class="place-items-center">
				<Dialog.Header>
					<Dialog.Title class="text-center">
						YOU ARE ABOUT TO DELETE THIS PROJECT.
					</Dialog.Title>
				</Dialog.Header>

				<Typography variant="body-md">
					Are you sure you want to delete this project?
				</Typography>

				<Dialog.Footer>
					<Button class="w-full" variant="destructive" on:click={() => deleteProject()}>
						If I click this, I am sure.
					</Button>
				</Dialog.Footer>
			</Dialog.Content>
		</Dialog.Root>
	{/if}
</form>
