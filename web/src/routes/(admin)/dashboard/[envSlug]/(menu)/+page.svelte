<script lang="ts">
	import * as Select from '$lib/components/ui/select';
	import SubmissionViewer from './submission-viewer.svelte';
	import type { Database, Tables } from '$lib/supabase';
	import type { SupabaseClient } from '@supabase/supabase-js';
	import { Toggle } from '$lib/components/ui/toggle';
	import { LocateOff, CheckCheck, LoaderCircle } from 'lucide-svelte';
	import { Button } from '$lib/components/ui/button';
	import { Typography } from '$lib/components/ui/typography';
	import { page } from '$app/stores';
	import { onMount } from 'svelte';
	import { browser } from '$app/environment';

	type Props = {
		data: {
			supabase: SupabaseClient<Database>;
			projects: Tables<'projects'>[];
		};
	};

	let { data }: Props = $props();

	const { supabase } = data;

	const STORAGE_KEY = 'selectedProjectId';

	let selectedProject: { label: string; value: string } | undefined = $state(undefined);

	// Initialize the selected project to be the selected project the last time the user was on the page
	const initializeSelectedProject = () => {
		if (!browser || data.projects.length === 0) return;

		const storedId = localStorage.getItem(STORAGE_KEY);
		const project = data.projects.find(p => p.id === storedId);

		if (!project || !data.projects[0]) return;

		selectedProject = project 
			? { label: project.title, value: project.id }
			: { label: data.projects[0].title, value: data.projects[0].id };
	};

	let submissions: Tables<'submissions'>[] = $state([]);

	supabase
		.channel('submissions')
		.on(
			'postgres_changes',
			{ event: 'INSERT', schema: 'public', table: 'submissions' },
			(payload) => {
				submissions.push(payload.new as Tables<'submissions'>);
			}
		)
		.subscribe();

	// Arbituarilly select the first submission
	let selectedSubmission: Tables<'submissions'> | null = $state(null);

	let relevantSubmissions: Tables<'submissions'>[] = $derived(
		submissions.filter((submission: Tables<'submissions'>) => submission.is_relevant === false)
	);

	let includeRead: boolean = $state(false);
	let includeIrrelevant: boolean = $state(false);

	let projectLoading = $state(false);

	const getSubmissionsFromDB = async (project_id: string) => {
		projectLoading = true;
		submissions = [];
		console.log(selectedProject);
		const { data, error } = await supabase
			.from('submissions')
			.select('*')
			.eq('project_id', project_id);
		if (error) {
			console.error(error);
		} else {
			console.log('data: ', data);
			submissions = data || [];
		}
		projectLoading = false;
	};

	// List that is displayed
	let displaySubmissions = $derived.by(() => {
		let _submissions: Tables<'submissions'>[] = [];

		if (!selectedProject) return _submissions;

		submissions.map((submission: Tables<'submissions'>) => {
			if (submission.project_id === selectedProject!.value) {
				if (!submission.is_relevant && includeIrrelevant) {
					_submissions.push(submission);
				}
				if (submission.done && includeRead) {
					_submissions.push(submission);
				}
				// If the submission is relevant and not done
				if (submission.is_relevant && !submission.done) {
					_submissions.push(submission);
				}
			}
		});

		// Ensure submission_created_utc is a valid date string and sort submissions by submission_created_utc
		_submissions.sort((a, b) => {
			const dateA = new Date(a.submission_created_utc).getTime();
			const dateB = new Date(b.submission_created_utc).getTime();
			return dateB - dateA; // Newest items first
		});

		return _submissions;
	});

	onMount(() => {
		initializeSelectedProject();
		if (selectedProject) {
			getSubmissionsFromDB(selectedProject.value);
		}
	});
</script>

{#if data.projects.length == 0}
	<div class="flex flex-col place-items-center gap-6">
		<Typography variant="headline-lg" class="text-center">No projects found</Typography>
		<Button class="w-fit" href="/dashboard/{$page.data.environment.slug}/projects">
			Create a new project
		</Button>
	</div>
{:else}
	<div class="grid grid-cols-6 grid-rows-5 gap-6 h-full">
		<div class="flex flex-col p-2 col-span-2 row-span-5">
			<div class="flex flex-col place-items-start w-full justify-between mb-4">
				<Select.Root
					portal={null}
					bind:selected={selectedProject}
					onSelectedChange={(project) => {
						console.log('changing project');
						project && getSubmissionsFromDB(project.value);
					}}
				>
					<div class="flex flex-row mb-4 gap-y-0.5 place-items-center gap-x-4 w-full">
						<Select.Label class="text-left pl-0">
							<Typography variant="headline-md" class="text-left">
								Project:
							</Typography>
						</Select.Label>
						<Select.Trigger class="border border-foreground text-primary w-[250px]">
							<Select.Value placeholder="Select a project" class="text-foreground" />
						</Select.Trigger>
						<Select.Content>
							<Select.Group>
								{#each data.projects as project}
									<Select.Item
										value={project.id}
										label={project.title}
										class="text-primary"
										on:click={() => browser && localStorage.setItem(STORAGE_KEY, project.id)}
									>
										{project.title}
									</Select.Item>
								{/each}
							</Select.Group>
						</Select.Content>
					</div>
				</Select.Root>
				<div class="flex flex-row gap-2">
					<Toggle variant="outline" bind:pressed={includeRead} class="gap-2">
						<CheckCheck /> Include Read
					</Toggle>
					<Toggle variant="outline" bind:pressed={includeIrrelevant} class="gap-2">
						<LocateOff /> Include Irrelevant
					</Toggle>
				</div>
			</div>

			<div class="h-fit mt-4 overflow-y-scroll flex flex-col gap-y-4">
				<Typography variant="headline-md" class="text-left">
					Submissions {!projectLoading ? '(' + displaySubmissions.length + ')' : ''}
					{#if projectLoading}
						<LoaderCircle class="animate-spin text-primary h-24 w-24" />
					{/if}
				</Typography>

				{#each displaySubmissions as submission}
					<Button
						class="text-wrap text-left h-fit mx-2 grid grid-cols-7 {selectedSubmission ==
						submission
							? 'bg-accent'
							: ''}"
						variant="outline"
						on:click={() => (selectedSubmission = submission)}
					>
						<div class="col-span-6 truncate">
							{submission.title}
						</div>
						<div class="ml-auto col-span-1">
							{#if submission.done}
								<CheckCheck class="w-5" />
							{/if}
							{#if !submission.is_relevant}
								<LocateOff class="w-5 " />
							{/if}
						</div>
					</Button>
				{/each}
			</div>
		</div>

		<div class="col-span-4 row-span-5">
			{#if selectedSubmission}
				<SubmissionViewer
					{supabase}
					bind:submission={selectedSubmission}
					bind:projectName={selectedProject.label}
				/>
			{:else}
				<div class="flex items-center justify-center p-6">
					<p class="text-muted-foreground">No submission selected</p>
				</div>
			{/if}
		</div>
	</div>
{/if}
