<script lang="ts">
	import { Button } from '$lib/components/ui/button';
	import * as Dialog from '$lib/components/ui/dialog';
	import * as Form from '$lib/components/ui/form';
	import { Input } from '$lib/components/ui/input';
	import { TagInput } from '$lib/components/ui/tag-input';
	import { projectSchema } from '$lib/schemas';
	import { LoaderCircle, Loader, ExternalLink, Loader2 } from 'lucide-svelte';
	import { superForm } from 'sveltekit-superforms';
	import { zodClient } from 'sveltekit-superforms/adapters';
	import { Typography } from '$lib/components/ui/typography';
	import { toast } from 'svelte-sonner';
	import { Switch } from '$lib/components/ui/switch';
	import { PUBLIC_CRITINO_URL } from '$env/static/public';
	import { goto } from '$app/navigation';
	import { TipTap } from '$lib/components/ui/tiptap';
	import { deleteProject as deleteProjectById } from '$lib/supabase/projects';
	import { generateHTML } from '@tiptap/core';
	import StarterKit from '@tiptap/starter-kit';
	import ScrollArea from '$lib/components/ui/scroll-area/scroll-area.svelte';
	import { fade, scale } from 'svelte/transition';

	let { data } = $props();

	let { supabase, environment, project } = data;
	let isToggling = $state(false);
	let isValidatingSubreddit = $state(false);

	const validateSubreddit = async (subreddit: string): Promise<boolean> => {
		isValidatingSubreddit = true;
		try {
			const response = await fetch(`https://www.reddit.com/r/${subreddit}/about.json`);
			const data = await response.json();
			
			if (response.ok && !data.error) {
				return true;
			} else {
				toast.error(`Subreddit r/${subreddit} does not exist`);
				return false;
			}
		} catch (error) {
			console.error('Error validating subreddit:', error);
			toast.error('Failed to validate subreddit');
			return false;
		} finally {
			isValidatingSubreddit = false;
		}
	};

	const form = superForm(data.projectForm, {
		dataType: 'json',
		delayMs: 400,
		timeoutMs: 3000,
		onSubmit: async () => {},
		validators: zodClient(projectSchema),
		resetForm: false,
		onUpdated({ form }) {
			if (form.message) {
				if (form.message.type == 'error') {
					toast.error(form.message.text);
				} else if (form.message.type == 'success') {
					toast.success(form.message.text);
					// Reset the loading state immediately after successful save
					$delayed = false;
					$timeout = false;
				}
			}
		},
	});

	const { form: formData, enhance, delayed, timeout } = form;

	$effect(() => {
		$formData = { ...project };
	});

	const toggleProject = async (newState: boolean) => {
		if (isToggling) return;
		
		isToggling = true;
		// Create a copy of the project with the new state
		const updatedProject = { ...project, running: newState };

		try {
			const response = await fetch(`/api/projects/${project.id}/toggle`, {
				method: 'POST',
				body: JSON.stringify({
					...updatedProject,
					environment_slug: environment!.slug
				}),
				headers: {
					'Content-Type': 'application/json'
				}
			});

			const result = await response.json();

			if (result.type === 'success') {
				// Update both the form data and the project reference
				$formData.running = newState;
				project.running = newState;
				toast.success(result.text);
			} else {
				toast.error(result.text || 'Failed to update project state');
			}
		} catch (error) {
			console.error('Error toggling project:', error);
			toast.error('Failed to update project state');
		} finally {
			isToggling = false;
		}
	};

	const deleteProject = async () => {
		const { error } = await deleteProjectById(project.id, { supabase });

		if (error) {
			console.log(error);

			toast.error('An error occurred. Try again.');
		} else {
			toast.success('Project successfully deleted.');
			goto(`/dashboard/${environment!.slug}/projects`);
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
		$formData.prompt = defaultPrompt;
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

<div class="flex gap-8">
	<div class="fixed">
		<Button variant="outline" href={`/dashboard/${environment!.slug}`} class="gap-2">
			<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="w-4 h-4"><path d="m12 19-7-7 7-7"/><path d="M19 12H5"/></svg>
			Back to Projects
		</Button>
	</div>
	<div class="flex-1 max-w-3xl mx-auto">
		<Typography as="h1" variant="headline-md" class="mb-4 text-center">Edit Project</Typography>

		<form method="POST" action="?/updateProject" class="flex flex-col gap-y-6" use:enhance>
			<input type="hidden" name="id" bind:value={$formData.id} />
			<input type="hidden" name="profile_id" bind:value={$formData.profile_id} />
			<!-- this button has to be here for disabling submit on enter when focusing on input fields-->
			<!-- https://github.com/sveltejs/kit/discussions/8657 -->
			<button type="submit" disabled style="display: none"></button>

			<Form.Field
				{form}
				name="running"
				class="flex flex-row items-center justify-between rounded-lg border p-4 transition-opacity duration-200 {isToggling ? 'opacity-50' : ''}"
			>
				<Form.Control let:attrs>
					<div class="flex flex-col gap-y-0.5">
						<div class="flex items-center gap-2 mt-1">
							<div
								class="h-3 w-3 rounded-full transition-colors
								{isToggling ? 'animate-pulse bg-gray-500' : $formData.running ? 'animate-pulse bg-emerald-500' : 'bg-orange-500'}"
							></div>
							{#if isToggling}
								<Typography variant="body-sm">Updating...</Typography>
							{:else}
								<Typography variant="body-sm">{$formData.running ? 'Project is running' : 'Project is paused'}</Typography>
							{/if}
						</div>						<Form.Description>
							Turn {!$formData.running ? 'on' : 'off'} to {!$formData.running ? 'start' : 'stop'} listening for Reddit posts.
						</Form.Description>
						
					</div>
					<div class="relative">
						<Switch 
							includeInput 
							{...attrs} 
							checked={$formData.running}
							onCheckedChange={(checked) => toggleProject(checked)}
							disabled={isToggling}
							class="data-[state=checked]:bg-emerald-500 transition-opacity duration-200 {isToggling ? 'opacity-50' : ''}"
						/>
						{#if isToggling}
							<div 
								class="absolute inset-0 flex items-center justify-center"
								in:fade={{ duration: 200 }}
								out:fade={{ duration: 150 }}
							>
								<div in:scale={{ duration: 200 }}>
									<Loader2 class="w-4 h-4 animate-spin text-foreground" />
								</div>
							</div>
						{/if}
					</div>
				</Form.Control>
			</Form.Field>

			<Form.Field {form} name="title">
				<Form.Control let:attrs>
					<div class="flex flex-col gap-y-1.5 items-start">
						<Form.Label>Title</Form.Label>
						<Form.Description>This is the project's title.</Form.Description>
					</div>
					<Input {...attrs} class="max-w-sm" bind:value={$formData.title} />
				</Form.Control>

				<Form.FieldErrors />
			</Form.Field>

			<Form.Field {form} name="subreddits" class="flex flex-col pb-0">
				<Form.Control let:attrs>
					<div class="flex flex-col gap-y-1.5 items-start">
						<Form.Label>Subreddits</Form.Label>
						<Form.Description>
							Manually add your subreddits, For example: "saas", "startups".
							<br />
							The cost of the project is proportional to the size and number of the subreddits
							you add.
						</Form.Description>
					</div>
					<TagInput
						bind:items={$formData.subreddits}
						placeholder="Type a subreddit here..."
						onNewItem={async (newSubreddit) => {
							const cleanSubreddit = newSubreddit.toLowerCase().trim().replace('r/', '');
							if (await validateSubreddit(cleanSubreddit)) {
								return cleanSubreddit;
							}
							return null;
						}}
						disabled={isValidatingSubreddit}
					/>
				</Form.Control>

				<Form.FieldErrors />
			</Form.Field>
			<Form.Field {form} name="prompt">
				<Form.Control let:attrs>
					<div class="flex flex-col gap-y-1.5 items-start">
					<Form.Label>Prompt</Form.Label>
					<Form.Description>
						Accurate results are achieved by providing a great prompt. <br />
						Tell the AI exactly what to look for.
					</Form.Description>
					<input type="hidden" name="prompt" bind:value={$formData.prompt} />
					</div>
					<Dialog.Root>
						<Dialog.Trigger>
							<Button variant="secondary" class="">Open Prompt</Button>
						</Dialog.Trigger>
						<Dialog.Content
							class="h-full min-h-96 w-full max-w-5xl grid-rows-[auto_1fr] place-items-center px-7"
						>
							<Button
								onclick={fillPromptWithTemplate}
								variant="outline"
								class="right-2 top-2"
							>
								Insert Example Prompt (Reletino's)
							</Button>

							<ScrollArea class="h-full w-full p-3">
								<TipTap
									class="h-full border border-input p-3 outline-input"
									bind:content={$formData.prompt}
								/>
							</ScrollArea>
						</Dialog.Content>
					</Dialog.Root>
					<Form.FieldErrors />
				</Form.Control>
			</Form.Field>
			<Form.Field {form} name="comment_style_prompt">
				<Form.Control let:attrs>
					<div class="flex flex-col gap-y-1.5 items-start">
					<Form.Label>Comment Style</Form.Label>
					<Form.Description>
						Define how the AI should style its comments when responding to relevant posts.
					</Form.Description>
					<input
						type="hidden"
						name="comment_style_prompt"
						bind:value={$formData.comment_style_prompt}
					/>
					</div>
					<Dialog.Root>
						<Dialog.Trigger>
							<Button variant="secondary" class="">Open Comment Style</Button>
						</Dialog.Trigger>
						<Dialog.Content
							class="h-full min-h-96 w-full max-w-5xl grid-rows-[auto_1fr] place-items-center px-7"
						>
							<Button
								onclick={fillCommentStyleWithTemplate}
								variant="outline"
								class="right-2 top-2"
							>
								Insert Example Comment Style
							</Button>
							<ScrollArea class="h-full w-full p-3">
								<TipTap
									class="h-full border border-input p-3 outline-input"
									bind:content={$formData.comment_style_prompt}
								/>
							</ScrollArea>
						</Dialog.Content>
					</Dialog.Root>
					<Form.FieldErrors />
				</Form.Control>
			</Form.Field>
			<Form.Field {form} name="dm_style_prompt">
				<Form.Control let:attrs>
					<div class="flex flex-col gap-y-1.5 items-start">
						<Form.Label>DM Style</Form.Label>
						<Form.Description>
							Define how the AI should style its direct messages when reaching out to users.
					</Form.Description>
					<input
						type="hidden"
						name="dm_style_prompt"
						bind:value={$formData.dm_style_prompt}
					/>
					<Dialog.Root>
						<Dialog.Trigger>
							<Button variant="secondary" class="">Open DM Style</Button>
						</Dialog.Trigger>
						<Dialog.Content
							class="h-full min-h-96 w-full max-w-5xl grid-rows-[auto_1fr] place-items-center px-7"
						>
							<Button
								onclick={fillDMStyleWithTemplate}
								variant="outline"
								class="right-2 top-2"
							>
								Insert Example DM Style
							</Button>
							<ScrollArea class="h-full w-full p-3">
								<TipTap
									class="h-full border border-input p-3 outline-input"
									bind:content={$formData.dm_style_prompt}
								/>
							</ScrollArea>
						</Dialog.Content>
					</Dialog.Root>
					<Form.FieldErrors />
				</Form.Control>
			</Form.Field>
			<div class="flex flex-col gap-y-2">
				<Form.Button class="mt-2" disabled={$timeout || $delayed}>
					{#if $timeout}
						<LoaderCircle class="animate-spin" />
					{:else if $delayed}
						<Loader class="animate-spin" />
					{:else}
						Save
					{/if}
				</Form.Button>
				<!-- <Button
					variant="secondary"
					href={`${PUBLIC_CRITINO_URL}/startino/reletino/${environment!.name}/${project.title}/workflows?key=${environment!.critino_key}`}
					target="_blank"
					class="w-full"
				>
					Manage Critiques
					<ExternalLink class="ml-2 w-5" />
				</Button> -->
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
			</div>
		</form>
	</div>
</div>
