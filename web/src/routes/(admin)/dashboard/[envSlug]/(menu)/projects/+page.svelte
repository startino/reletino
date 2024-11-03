<script lang="ts">
	import Button from '$lib/components/ui/button/button.svelte';
	import Typography from '$lib/components/ui/typography/typography.svelte';

	import type { Tables } from '$lib/supabase';
	import { EntityControlGrid } from '$lib/components/ui/entity-control-grid';
	import { Pen } from 'lucide-svelte';
	import { getEnvironmentState } from '$lib/states';

	let { data } = $props();

	let { session, projects: dataProjects } = data;

	const env = getEnvironmentState();

	let projects: Tables<'projects'>[] = $state(dataProjects || []);
	let selectedProjectId: string = $state('');

	let newProject: Tables<'projects'> | null = $state(null);
	let baseURL = `/dashboard/${env.value?.name}/projects`;
</script>

<div class="flex flex-col gap-8">
	<Typography variant="display-lg">Projects</Typography>

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
			<div class="bg-card relative grid gap-4">
				<Button
					class=" flex h-full w-full flex-col p-8 py-12 pb-10 pt-3"
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
					<a
						class="z-20 rounded-full"
						href="{baseURL}/{project.id}/edit"
						aria-label="Edit project"
					>
						<Pen size="20" class=" transition-all hover:scale-125" />
					</a>
				</div>
			</div>
		{/snippet}
	</EntityControlGrid>
</div>
