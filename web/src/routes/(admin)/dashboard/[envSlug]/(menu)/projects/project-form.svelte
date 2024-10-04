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
							class="flex w-full flex-row justify-between rounded-md bg-card px-2 py-1 hover:bg-destructive/20"
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
				Find prompt guides
				<a
					class="text-primary underline"
					href="https://reletino.notion.site/"
					target="_blank"
				>
					here
				</a>
			</Form.Description>
			<input type="hidden" name="prompt" bind:value={$formData.prompt} />
			<Dialog.Root>
				<Dialog.Trigger>
					<Button variant="secondary" class="">Open Prompt</Button>
				</Dialog.Trigger>
				<Dialog.Content class="h-full min-h-96 w-full max-w-5xl place-items-center px-7">
					<Textarea {...attrs} rows={35} bind:value={$formData.prompt} />
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
		href={`${PUBLIC_CRITINO_URL}/startino/reletino/${environment.name}/${selectedProject.title}/workflows`}
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
