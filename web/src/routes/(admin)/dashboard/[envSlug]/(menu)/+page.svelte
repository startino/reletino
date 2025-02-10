<script lang="ts">
	import Button from '$lib/components/ui/button/button.svelte';
	import Typography from '$lib/components/ui/typography/typography.svelte';

	import type { Tables } from '$lib/supabase';
	import { EntityControlGrid } from '$lib/components/ui/entity-control-grid';
	import { Pen, Trash, Trash2, X, Loader2 } from 'lucide-svelte';
	import { getEnvironmentState } from '$lib/states';
	import { deleteProject } from '$lib/supabase/projects';
	import { goto } from '$app/navigation';
	import { Switch } from '$lib/components/ui/switch';
	import { toast } from 'svelte-sonner';
	import { fade, scale } from 'svelte/transition';

	let { data } = $props();

	let { session, projects: dataProjects, supabase } = data;

	const env = getEnvironmentState();

	let projects: Tables<'projects'>[] = $state(dataProjects || []);
	let entities = $derived(projects.map((p) => ({ ...p, name: p.title, description: p.title })));
	let loadingProjects = $state<string[]>([]);

	let baseURL = `/dashboard/${env.value?.slug}`;

	const toggleProject = async (project: Tables<'projects'>) => {
		if (loadingProjects.includes(project.id)) return;
		
		loadingProjects = [...loadingProjects, project.id];
		const newState = !project.running;
		
		// Create a copy of the project to avoid mutating state before success
		const updatedProject = { ...project, running: newState };
		
		try {
			const response = await fetch(`/api/projects/${project.id}/toggle`, {
				method: 'POST',
				body: JSON.stringify({
					...updatedProject,
					environment_slug: env.value?.slug
				}),
				headers: {
					'Content-Type': 'application/json'
				}
			});

			const result = await response.json();

			if (result.type === 'success') {
				// Find and update the project in the array
				const index = projects.findIndex(p => p.id === project.id);
				if (index !== -1) {
					projects[index] = updatedProject;
					// Force reactivity update
					projects = [...projects];
				}
				toast.success(result.text);
			} else {
				toast.error(result.text || 'Failed to update project state');
			}
		} catch (error) {
			console.error('Error toggling project:', error);
			toast.error('Failed to update project state');
		} finally {
			loadingProjects = loadingProjects.filter(id => id !== project.id);
		}
	};
</script>

<svelte:head>
	<title>Projects</title>
</svelte:head>

<div class="flex flex-col gap-8">
	<Typography variant="display-sm" class="text-left ml-10">Projects</Typography>

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
			<div class="relative grid gap-4 bg-card rounded-lg transition-opacity duration-200 {loadingProjects.includes(project.id) ? 'opacity-50 pointer-events-none' : ''}">
				<Button
					class="flex h-full w-full flex-col p-8 py-12 pb-16 pt-3 {loadingProjects.includes(project.id) ? 'opacity-50' : 'hover:bg-accent/50'} transition-colors"
					href="{baseURL}/{project.id}"
					variant="ghost"
				>
					<div class="mb-4 ml-auto flex flex-row place-items-center gap-x-2">
						<div
							class="h-3 w-3 rounded-full transition-colors
							{loadingProjects.includes(project.id) ? 'animate-pulse bg-gray-500' : project.running ? 'animate-pulse bg-emerald-500' : 'bg-orange-500'}"
						></div>
						{#if loadingProjects.includes(project.id)}
							<Typography variant="body-sm">Updating...</Typography>
						{:else}
							{#if project.running}
								<Typography variant="body-sm">Running</Typography>
							{:else}
								<Typography variant="body-sm">Paused</Typography>
							{/if}
						{/if}
					</div>
					<Typography variant="title-lg">{project.title}</Typography>
				</Button>

				<div class="absolute bottom-3 left-4 flex items-center gap-2">
					<div class="relative">
						<Switch
							checked={project.running}
							onCheckedChange={() => toggleProject(project)}
							disabled={loadingProjects.includes(project.id)}
							class="data-[state=checked]:bg-emerald-500 transition-opacity duration-200 {loadingProjects.includes(project.id) ? 'opacity-50' : ''}"
						/>
						{#if loadingProjects.includes(project.id)}
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

					<Button
						class="group"
						size="icon"
						variant="ghost"
						href="{baseURL}/{project.id}/edit"
						aria-label="Edit project"
						disabled={loadingProjects.includes(project.id)}
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
						disabled={loadingProjects.includes(project.id)}
					>
						<Trash2 size="20" class="transition-all text-red-700 group-hover:scale-110" />
					</Button>
				</div>
			</div>
		{/snippet}
	</EntityControlGrid>
</div>
