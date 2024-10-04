<script lang="ts">
	import Button from '$lib/components/ui/button/button.svelte';
	import * as Dialog from '$lib/components/ui/dialog';
	import Typography from '$lib/components/ui/typography/typography.svelte';

	import type { Tables } from '$lib/supabase';
	import type { SuperValidated, Infer } from 'sveltekit-superforms';
	import type { ProjectSchema } from '$lib/schemas';
	import ProjectForm from './project-form.svelte';
	import type { Session, SupabaseClient } from '@supabase/supabase-js';

	interface Props {
		data: {
			supabase: SupabaseClient<any, 'public', any>;
			environment: Tables<'environments'>;
			session: Session;
			projects: Tables<'projects'>[];
			projectForm: SuperValidated<Infer<ProjectSchema>>;
		};
	}

	let { data }: Props = $props();

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
	<ul class="grid grid-cols-3 gap-4">
		<li class="col-span-3 mx-auto">
			<Button
				class=""
				onclick={() => {
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
				Create New Project
			</Button>
		</li>
		{#each projects as project}
			<li class="rounded-md bg-card">
				<Button
					class="flex h-full w-full flex-col p-8 py-12 pt-3"
					variant="ghost"
					onclick={() => {
						selectedProjectId = project.id;
					}}
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
			</li>
		{/each}
	</ul>
</div>
