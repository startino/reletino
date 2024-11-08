<script lang="ts">
	import { Button } from '$lib/components/ui/button';
	import * as Dialog from '$lib/components/ui/dialog';
	import * as Form from '$lib/components/ui/form';
	import { Input } from '$lib/components/ui/input';
	import { TagInput } from '$lib/components/ui/tag-input';
	import { projectSchema } from '$lib/schemas';
	import { LoaderCircle, Loader, ExternalLink } from 'lucide-svelte';
	import { superForm } from 'sveltekit-superforms';
	import { zodClient } from 'sveltekit-superforms/adapters';
	import { Typography } from '$lib/components/ui/typography';
	import { toast } from 'svelte-sonner';
	import { Switch } from '$lib/components/ui/switch';
	import { PUBLIC_CRITINO_URL } from '$env/static/public';
	import { goto } from '$app/navigation';
	import { deleteProject as deleteProjectById } from '$lib/supabase/projects';

	let { data } = $props();

	let { supabase, environment, project } = data;

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
				}
			}
		},
	});

	const { form: formData, enhance, delayed, timeout } = form;

	$effect(() => {
		$formData = { ...project, context: project.context as any };
	});

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
</script>

<div class="mx-auto max-w-3xl">
	<Typography as="h1" variant="headline-md" class="mb-4 text-center">Edit Project</Typography>

	<form method="POST" action="?/updateProject" class="flex flex-col gap-y-2" use:enhance>
		<input type="hidden" name="id" bind:value={$formData.id} />
		<input type="hidden" name="profile_id" bind:value={$formData.profile_id} />
		<!-- this button has to be here for disabling submit on enter when focusing on input fields-->
		<!-- https://github.com/sveltejs/kit/discussions/8657 -->
		<button type="submit" disabled style="display: none"></button>

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
				<TagInput
					bind:items={$formData.subreddits}
					placeholder="Type a subreddit here..."
					onNewItem={(newSubreddit) =>
						newSubreddit.toLowerCase().trim().replace('r/', '')}
				/>
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
					<Form.Control>
						<Form.Label>Irrelevant Post Examples</Form.Label>

						<TagInput
							bind:items={$formData.context.irrelevant_post_examples}
							placeholder="Add example"
						/>

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
					<Form.Control>
						<Form.Label>Core Features</Form.Label>

						<TagInput
							bind:items={$formData.context.core_features}
							placeholder="Add feature"
						/>

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
					<Form.Description>
						Turn on to start listening for Reddit posts.
					</Form.Description>
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
			href={`${PUBLIC_CRITINO_URL}/startino/reletino/${environment!.name}/${project.title}/workflows?key=${environment!.critino_key}`}
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
	</form>
</div>
