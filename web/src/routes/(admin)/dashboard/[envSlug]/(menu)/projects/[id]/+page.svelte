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

	let { data } = $props();

	const { supabase, project } = data;

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
		console.log(project);
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

		submissions.map((submission: Tables<'submissions'>) => {
			if (submission.project_id === project.id) {
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
		getSubmissionsFromDB(project.id);
	});
</script>

<div class="grid h-full grid-cols-5 grid-rows-5 gap-6">
	<div class="col-span-2 row-span-5 flex flex-col p-2">
		<div class="mb-4 flex w-full flex-col place-items-start justify-between gap-4">
			<Typography as="h1" variant="headline-lg">{project.title}</Typography>
			<div class="flex flex-row gap-2">
				<Toggle variant="outline" bind:pressed={includeRead} class="gap-2">
					<CheckCheck /> Include Read
				</Toggle>
				<Toggle variant="outline" bind:pressed={includeIrrelevant} class="gap-2">
					<LocateOff /> Include Irrelevant
				</Toggle>
			</div>
		</div>

		<div class="mt-4 flex h-fit flex-col gap-y-4 overflow-y-scroll">
			<Typography variant="headline-md" class="text-left">
				Submissions {!projectLoading ? '(' + displaySubmissions.length + ')' : ''}
				{#if projectLoading}
					<LoaderCircle class="text-primary h-24 w-24 animate-spin" />
				{/if}
			</Typography>

			{#each displaySubmissions as submission}
				<Button
					class="mx-2 grid h-fit grid-cols-7 text-wrap text-left {selectedSubmission ==
					submission
						? 'bg-accent'
						: ''}"
					variant="outline"
					on:click={() => (selectedSubmission = submission)}
				>
					<div class="col-span-6 truncate">
						{submission.title}
					</div>
					<div class="col-span-1 ml-auto">
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

	<div class="col-span-3 row-span-5">
		{#if selectedSubmission}
			<SubmissionViewer
				{supabase}
				bind:submission={selectedSubmission}
				bind:projectName={project.title}
			/>
		{:else}
			<div class="flex items-center justify-center p-6">
				<p class="text-muted-foreground">No submission selected</p>
			</div>
		{/if}
	</div>
</div>
