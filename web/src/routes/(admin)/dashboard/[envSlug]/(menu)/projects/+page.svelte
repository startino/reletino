<script lang="ts">
	import Button from '$lib/components/ui/button/button.svelte';
	import * as Dialog from '$lib/components/ui/dialog';
	import Typography from '$lib/components/ui/typography/typography.svelte';

	import type { Tables } from '$lib/supabase';
	import ProjectForm from './project-form.svelte';
	import { EntityControlGrid } from '$lib/components/ui/entity-control-grid';

	let { data } = $props();

	let { supabase, session, environment, projects: dataProjects } = data;

	let projects: Tables<'projects'>[] = $state(dataProjects || []);
	let selectedProjectId: string = $state('');

	let newProject: Tables<'projects'> | null = $state(null);
</script>

<div class="flex flex-col gap-8">
	<Typography variant="display-lg">Projects</Typography>
	<Dialog.Root
		open={selectedProjectId != ''}
		onOpenChange={(open) => {
			if (!open) {
				selectedProjectId = '';
			}
		}}
	>
		<Dialog.Content class="w-full max-w-5xl">
			<Dialog.Header>
				<Dialog.Title>Project</Dialog.Title>
			</Dialog.Header>
			{#if selectedProjectId != ''}
				<ProjectForm
					{session}
					{supabase}
					{environment}
					projectForm={data.projectForm}
					bind:projects
					bind:selectedProjectId
					bind:newProject
				/>
			{/if}
		</Dialog.Content>
	</Dialog.Root>

	<EntityControlGrid
		entities={projects.map((p) => ({ ...p, name: p.title, description: p.title }))}
		name="Project"
		oncreate={() => {
			newProject = {
				id: crypto.randomUUID(),
				profile_id: session.user.id,
				created_at: new Date().toISOString(),
				title: 'Untitled Project',
				prompt: '',
				running: false,
				subreddits: [],
			};
			selectedProjectId = newProject.id;
		}}
	>
		{#snippet itemCell(project)}
			<Button
				class="bg-card flex h-full w-full flex-col p-8 py-12 pt-3"
				variant="ghost"
				href="/dashboard/{environment?.name}/projects/{project.id}"
			>
				<div class="mb-4 ml-auto flex flex-row place-items-center gap-x-2">
					<div
						class="h-3 w-3 rounded-full {project.running
							? 'animate-pulse bg-emerald-500'
							: 'bg-orange-500'}"
					></div>
					{#if project.running}
						<Typography variant="body-sm">Running</Typography>
					{:else}
						<Typography variant="body-sm">Paused</Typography>
					{/if}
				</div>
				<Typography variant="title-lg">{project.title}</Typography>
			</Button>
		{/snippet}
	</EntityControlGrid>
</div>
