<script lang="ts">
	import { Button } from '$lib/components/ui/button';
	import { Badge } from '$lib/components/ui/badge';
	import * as Dialog from '$lib/components/ui/dialog';
	import * as Form from '$lib/components/ui/form';
	import { Input } from '$lib/components/ui/input';
	import { projectSchema, type ProjectSchema } from '$lib/schemas';
	import { LoaderCircle, Loader, ExternalLink, Plus } from 'lucide-svelte';
	import type { Database, Tables } from '$lib/supabase';
	import { superForm, type SuperValidated, type Infer } from 'sveltekit-superforms';
	import { zodClient } from 'sveltekit-superforms/adapters';
	import { X } from 'lucide-svelte';
	import { Typography } from '$lib/components/ui/typography';
	import { toast } from 'svelte-sonner';
	import type { SupabaseClient } from '@supabase/supabase-js';
	import { Switch } from '$lib/components/ui/switch';
	import { PUBLIC_CRITINO_URL } from '$env/static/public';
	import { TipTap } from '$lib/components/ui/tiptap';
	import { generateHTML } from '@tiptap/core';
	import StarterKit from '@tiptap/starter-kit';
	import { goto } from '$app/navigation';
	import { deleteProject as deleteProjectById } from '$lib/supabase/projects';

	interface Props {
		supabase: SupabaseClient<Database>;
		projectForm: SuperValidated<Infer<ProjectSchema>>;
		environment: Tables<'environments'>;
		project: Tables<'projects'>;
	}

	let { supabase, environment, projectForm, project = $bindable() }: Props = $props();
	let irrelevantPostExample = $state('');
	let coreFeature = $state('');

	const form = superForm(projectForm, {
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
				}
			}
		},
	});

	const { form: formData, errors, enhance, message, delayed, timeout } = form;

	$effect(() => {
		$formData = project;
	});

	$inspect($formData);

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
		const { error } = await deleteProjectById(project.id, { supabase });

		if (error) {
			console.log(error);

			toast.error('An error occurred. Try again.');
		} else {
			toast.success('Project successfully deleted.');
			goto(`/dashboard/${environment.name}/projects`);
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
					{#each $formData.subreddits as subreddits}
						<input name={attrs.name} hidden value={subreddits} />
					{/each}

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

	<div>
		{#if $formData.context.category == 'find-leads'}
			<Typography as="h2" variant="body-md" class="font-bold">
				Lead Finding Configuration
			</Typography>
			<Form.Field {form} name="context.product_name">
				<Form.Control let:attrs>
					<Form.Label>Project Name</Form.Label>
					<Input {...attrs} bind:value={$formData.context.product_name} />
					<Form.FieldErrors />
				</Form.Control>
			</Form.Field>

			<Form.Field {form} name="context.icp">
				<Form.Control let:attrs>
					<Form.Label>ICP</Form.Label>
					<Input {...attrs} bind:value={$formData.context.icp} />
					<Form.FieldErrors />
				</Form.Control>
			</Form.Field>

			<Form.Field {form} name="context.irrelevant_post_examples">
				<Form.Control let:attrs>
					<Form.Label>Irrelevant Post Examples</Form.Label>
					<div class="flex gap-2">
						<Input
							bind:value={irrelevantPostExample}
							placeholder="Add example"
							onkeydown={(e) => {
								if (e.key === 'Enter') {
									e.preventDefault();
									if (irrelevantPostExample) {
										$formData.context.category === 'find-leads' &&
											($formData.context.irrelevant_post_examples = [
												...$formData.context.irrelevant_post_examples,
												irrelevantPostExample,
											]);
										irrelevantPostExample = '';
									}
								}
							}}
						/>
						<Button
							type="button"
							variant="outline"
							onclick={() => {
								if (irrelevantPostExample) {
									$formData.context.category === 'find-leads' &&
										($formData.context.irrelevant_post_examples = [
											...$formData.context.irrelevant_post_examples,
											irrelevantPostExample,
										]);
									irrelevantPostExample = '';
								}
							}}
						>
							<Plus />
						</Button>
					</div>
					{#if $formData.context.irrelevant_post_examples.length > 0}
						<div class="flex flex-wrap gap-2">
							{#each $formData.context.irrelevant_post_examples as example, idx}
								<Badge variant="outline" class="gap-1.5">
									{example}
									<button
										type="button"
										class="hover:text-destructive"
										onclick={() => {
											$formData.context.category === 'find-leads' &&
												($formData.context.irrelevant_post_examples =
													$formData.context.irrelevant_post_examples.filter(
														(_, i) => i !== idx
													));
										}}
									>
										<X class="h-3 w-3" />
									</button>
								</Badge>
							{/each}
						</div>
					{/if}
					<Form.FieldErrors />
				</Form.Control>
			</Form.Field>
		{:else if $formData.context.category == 'find-competition'}
			<Typography as="h2" variant="body-md" class="font-bold">
				Competition Finding Configuration
			</Typography>

			<Form.Field {form} name="context.product_name">
				<Form.Control let:attrs>
					<Form.Label>Name</Form.Label>
					<Input {...attrs} bind:value={$formData.context.name} />
					<Form.FieldErrors />
				</Form.Control>
			</Form.Field>

			<Form.Field {form} name="context.core_features">
				<Form.Control let:attrs>
					<Form.Label>Core Features</Form.Label>
					<div class="flex gap-2">
						<Input
							bind:value={coreFeature}
							placeholder="Add feature"
							onkeydown={(e) => {
								if (e.key === 'Enter') {
									e.preventDefault();
									if (coreFeature) {
										$formData.context.category === 'find-competition' &&
											($formData.context.core_features = [
												...$formData.context.core_features,
												coreFeature,
											]);
										coreFeature = '';
									}
								}
							}}
						/>
						<Button
							type="button"
							variant="outline"
							onclick={() => {
								if (coreFeature) {
									$formData.context.category === 'find-competition' &&
										($formData.context.core_features = [
											...$formData.context.core_features,
											coreFeature,
										]);
									coreFeature = '';
								}
							}}
						>
							<Plus />
						</Button>
					</div>
					{#if $formData.context.core_features.length > 0}
						<div class="flex flex-wrap gap-2">
							{#each $formData.context.core_features as feature, idx}
								<Badge variant="outline" class="gap-1.5">
									{feature}
									<button
										type="button"
										class="hover:text-destructive"
										onclick={() => {
											$formData.context.category === 'find-leads' &&
												($formData.context.irrelevant_post_examples =
													$formData.context.irrelevant_post_examples.filter(
														(_, i) => i !== idx
													));
										}}
									>
										<X class="h-3 w-3" />
									</button>
								</Badge>
							{/each}
						</div>
					{/if}
					<Form.FieldErrors />
				</Form.Control>
			</Form.Field>
		{/if}
	</div>

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
		href={`${PUBLIC_CRITINO_URL}/startino/reletino/${environment.name}/${project.title}/workflows?key=${environment.critino_key}`}
		target="_blank"
		class="w-full"
	>
		Manage Critiques
		<ExternalLink class="ml-2 w-5" />
	</Button>
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

			<Typography variant="body-md">Are you sure you want to delete this project?</Typography>

			<Dialog.Footer>
				<Button class="w-full" variant="destructive" on:click={() => deleteProject()}>
					If I click this, I am sure.
				</Button>
			</Dialog.Footer>
		</Dialog.Content>
	</Dialog.Root>
</form>
