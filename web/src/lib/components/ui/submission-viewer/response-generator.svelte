<script lang="ts">
	import { Textarea } from '$lib/components/ui/textarea';
	import { toast } from 'svelte-sonner';
	import type { Tables } from '$lib/supabase';
	import { PUBLIC_API_URL } from '$env/static/public';
	import { Copy, LoaderCircle, ThumbsUp } from 'lucide-svelte';
	import { handleCommentOrDmCritique } from '$lib/apis/critino';
	import { page } from '$app/stores';
	import { Button } from '$lib/components/ui/button';
	import type { SupabaseClient } from '@supabase/supabase-js';
	import { Switch } from '$lib/components/ui/switch';
	import { Typography } from '$lib/components/ui/typography';

	type Props = {
		supabase: SupabaseClient<any, 'public', any>;
		submission: Tables<'submissions'>;
		projectId: string;
		projectName: string;
	};

	let { submission = $bindable(), projectId, projectName, supabase }: Props = $props();

	let generating = $state(false);
	let commentResponse = $state(submission.approved_comment || '');
	let dmResponse = $state(submission.approved_dm || '');
	let feedbackLoading = $state(false);
	let isDmSelected = $state(false);
	let feedback = $state('');

	const handleApprove = async () => {
		const response = isDmSelected ? dmResponse : commentResponse;

		await handleCommentOrDmCritique({
			submission,
			response: response,
			optimal: response,
			projectName: projectName,
			teamName: $page.data.environment.name,
			isDm: isDmSelected,
		});

		const { data, error } = await supabase
			.from('submissions')
			.update({
				approved_dm: isDmSelected ? response : submission.approved_dm,
				approved_comment: !isDmSelected ? response : submission.approved_comment,
			})
			.eq('id', submission.id)
			.select('*');

		if (error || !data) {
			toast.error('Failed to approve evaluation');
			return;
		}

		if (isDmSelected) {
			submission.approved_dm = response;
		} else {
			submission.approved_comment = response;
		}

		toast.success('Response approved');
	};

	async function generateResponse() {
		generating = true;
		try {
			console.log('Generating response with:', {
				project_id: projectId,
				submission_title: submission.title,
				submission_selftext: submission.selftext,
				is_dm: isDmSelected,
			});
			const res = await fetch(`${PUBLIC_API_URL}/generate-response`, {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
				},
				body: JSON.stringify({
					author_name: submission.author,
					project_id: projectId,
					submission_title: submission.title,
					submission_selftext: submission.selftext,
					team_name: $page.data.environment.name,
					is_dm: isDmSelected,
					feedback: `Feedback: \n ${feedback} \n\n This was the previous generated response: \n ${isDmSelected ? dmResponse : commentResponse}`,
				}),
			});

			if (!res.ok) {
				const text = await res.text();
				console.error('Response not OK:', res.status, text);
				throw new Error(`HTTP error! status: ${res.status}`);
			}

			const data = await res.json();
			console.log('Response data:', data);

			if (data.status === 'success') {
				if (isDmSelected) {
					dmResponse = data.response;
				} else {
					commentResponse = data.response;
				}
				toast.success('Response generated successfully');
			} else {
				toast.error('Failed to generate response', {
					description: data.message,
				});
			}
		} catch (error) {
			console.error('Error generating response:', error);
			toast.error('Failed to generate response');
		} finally {
			generating = false;
		}
	}
</script>

<div class="grid grid-cols-5 gap-4">
	<div class="col-span-2 grid grid-cols-3 gap-2">
		<div class="flex flex-col items-center gap-4">
			<div class="flex flex-row gap-2">
				<Button
					on:click={() => handleApprove()}
					disabled={feedbackLoading ||
						(isDmSelected ? submission.approved_dm : submission.approved_comment)}
					size="icon"
					variant="outline"
					class="flex items-center gap-2 border-green-600 text-green-600 hover:bg-green-600/40 hover:text-white"
				>
					{#if feedbackLoading}
						<LoaderCircle class="h-5 w-5 animate-spin" />
					{:else}
						<ThumbsUp class="h-5 w-5" />
					{/if}
				</Button>
				<Button
					variant="outline"
					size="icon"
					class=""
					disabled={dmResponse === '' && commentResponse === ''}
					on:click={() => {
						navigator.clipboard.writeText(dmResponse);
						toast.success('Response copied to clipboard');
					}}
				>
					<Copy class="h-5 w-5" />
				</Button>
			</div>
			<div class="col-span-2 flex w-full flex-col items-center">
				<Switch bind:checked={isDmSelected} />
				<Typography variant="body-sm" class="text-center">
					{isDmSelected ? 'DM' : 'Comment'}
				</Typography>
			</div>
			<Button class="" disabled={generating} on:click={() => generateResponse()}>
				{#if generating}
					<LoaderCircle class="mr-1 h-5 w-5 animate-spin" />
					Generating
				{:else}
					{isDmSelected
						? dmResponse
							? 'Regenerate'
							: 'Generate'
						: commentResponse
							? 'Regenerate'
							: 'Generate'}
				{/if}
			</Button>
		</div>
		<div class="col-span-2 flex w-full flex-col gap-1">
			<Typography variant="title-sm" class="mt-0 pt-0 text-start">Feedback</Typography>
			<Textarea id="response-feedback" bind:value={feedback} rows={3} class="h-full w-full" />
		</div>
	</div>
	<div class="col-span-3 flex w-full flex-col gap-1">
		<Typography variant="title-sm" class="mt-0 pt-0 text-start">Response</Typography>

		{#if isDmSelected}
			<Textarea
				id="comment-response"
				bind:value={dmResponse}
				rows={6}
				disabled={submission.approved_dm}
				class="col-span-3 w-full"
			/>
		{:else}
			<Textarea
				id="comment-response"
				bind:value={commentResponse}
				rows={6}
				disabled={submission.approved_comment}
				class="col-span-3 w-full"
			/>
		{/if}
	</div>
</div>
