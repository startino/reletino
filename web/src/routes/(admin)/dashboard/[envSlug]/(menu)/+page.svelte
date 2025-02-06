<script lang="ts">
	import Button from '$lib/components/ui/button/button.svelte';
	import Typography from '$lib/components/ui/typography/typography.svelte';

	import type { Tables } from '$lib/supabase';
	import { EntityControlGrid } from '$lib/components/ui/entity-control-grid';
	import { Pen, Trash, Trash2, X } from 'lucide-svelte';
	import { getEnvironmentState } from '$lib/states';
	import { deleteProject } from '$lib/supabase/projects';
	import { goto } from '$app/navigation';

	let { data } = $props();

	let { session, projects: dataProjects, supabase } = data;

	const env = getEnvironmentState();

	let projects: Tables<'projects'>[] = $state(dataProjects || []);
	let entities = $derived(projects.map((p) => ({ ...p, name: p.title, description: p.title })));

	let baseURL = `/dashboard/${env.value?.slug}`;
</script>

<svelte:head>
	<title>Projects</title>
</svelte:head>

<div class="flex flex-col gap-8">
	<Typography variant="display-sm" class="">Projects</Typography>

	<EntityControlGrid
		{entities}
		name="Project"
		oncreate={() => {
			goto(`${baseURL}/create`);
		}}
		ondelete={(idx) => {
			const [project] = projects.splice(idx, 1);
			deleteProject(project!.id, { supabase });
		}}
	>
		{#snippet itemCell(project, { deleteEntity })}
			<div class="relative grid gap-4 bg-card rounded-lg">
				<Button
					class="flex h-full w-full flex-col p-8 py-12 pb-16 pt-3 hover:bg-accent/50"
					href="{baseURL}/{project.id}"
					variant="ghost"
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

				<div class="absolute bottom-3 left-4 flex">
					<Button
						class="group"
						size="icon"
						variant="ghost"
						href="{baseURL}/{project.id}/edit"
						aria-label="Edit project"
					>
						<Pen size="20" class="transition-all group-hover:scale-110" />
					</Button>

					<Button
						class="group"
						size="icon"
						variant="ghost"
						onclick={() => {
							deleteEntity();
						}}
					>
						<Trash2 size="20" class="transition-all text-red-700 group-hover:scale-110" />
					</Button>
				</div>
			</div>
		{/snippet}
	</EntityControlGrid>
</div>
