<script lang="ts">
	import { format, formatDistanceToNowStrict } from 'date-fns';
	import { Button, buttonVariants } from '$lib/components/ui/button';
	import { Separator } from '$lib/components/ui/separator';
	import { Textarea } from '$lib/components/ui/textarea';
	import * as Dialog from '$lib/components/ui/dialog';
	import critino from '$lib/apis/critino';
	import { goto } from '$app/navigation';
	import { page } from '$app/stores';

	import type { Tables } from '$lib/supabase';

	import { toast } from 'svelte-sonner';

	import { enhance } from '$app/forms';
	import { Typography } from '$lib/components/ui/typography';
	import type { SupabaseClient } from '@supabase/supabase-js';
	import { CheckCheck, ExternalLink, LoaderCircle, Undo, ThumbsUp, ThumbsDown } from 'lucide-svelte';
	import { PUBLIC_CRITINO_API_KEY, PUBLIC_OPENROUTER_API_KEY } from '$env/static/public';
	import ResponseGenerator from './response-generator.svelte';
	import { handleCritique } from '$lib/apis/critino';

	type Props = {
		supabase: SupabaseClient<any, 'public', any>;
		submission: Tables<'submissions'>;
		projectName: string;
	}

	let { supabase, submission = $bindable(), projectName = $bindable() }: Props = $props();

	// Reactive UI
	let critinoLoading = $state(false);
	let markingAsRead = $state(false);
	let updatedReasoning = $state('');
	let showUpdateDialog = $state(false);

	// Function to copy to clipboard so I can easily copy this to my sales
	// management Google Sheet :P
	async function copyToClipboard(submission: Tables<'submissions'>) {
		try {
			const currentDate = new Date();
			const formattedDate = `${currentDate.getDate()}/${currentDate.getMonth() + 1}`;
			const cells = [submission.author, submission.url, '', formattedDate];
			// "	" is the special key that Google sheets uses to separate cells.
			// Select the text to actually see the character s`in`ce my theme can't see
			// it by default lol
			await navigator.clipboard.writeText(cells.join('	'));
			toast.success('submission Copied', {
				description: '',
			});
		} catch (err) {
			console.error('Failed to copy: ', err);
		}
	}

	async function markAsRead() {
		markingAsRead = true;
		const { data, error } = await supabase
			.from('submissions')
			.update({
				done: true,
			})
			.eq('id', submission.id)
			.select('*');
		if (error || !data) {
			toast.error('Failed to mark as read');
		}
		submission.done = true;
		markingAsRead = false;
		toast.success('Marked as read');
	}

	const handleCritiqueClick = async (submission: Tables<'submissions'>, isGood: boolean) => {
		if (!isGood) {
			showUpdateDialog = true;
			updatedReasoning = submission.reasoning;
			return;
		}

		critinoLoading = true;
		const res = await handleCritique(
			submission, 
			projectName, 
			$page.data.environment.name,
			'', // context
			isGood ? submission.reasoning : '', // if good, use existing reasoning as optimal
			isGood ? '' : submission.reasoning, // if bad, use existing reasoning as example of what not to do
			`This is an example of a ${isGood ? 'good' : 'bad'} response. ${isGood ? 'The reasoning is clear and accurate.' : 'The reasoning needs improvement.'}`
		);
		critinoLoading = false;

		if (!res) return;

		if (res.url) {
			window.open(res.url + '?key=' + PUBLIC_CRITINO_API_KEY, '_blank');
		}
	};

	const handleUpdateReasoning = async () => {
		critinoLoading = true;
		showUpdateDialog = false;

		// First update the submission reasoning
		const { error } = await supabase
			.from('submissions')
			.update({
				reasoning: updatedReasoning
			})
			.eq('id', submission.id);

		if (error) {
			toast.error('Failed to update reasoning');
			critinoLoading = false;
			return;
		}

		// Then create the critique
		const res = await handleCritique(
			{ ...submission, reasoning: updatedReasoning },
			projectName,
			$page.data.environment.name,
			'', // context
			'', // not good, so no optimal
			updatedReasoning, // use updated reasoning as example of what not to do
			'This is an example of a bad response. The reasoning needs improvement.'
		);
		critinoLoading = false;

		if (!res) return;

		if (res.url) {
			window.open(res.url + '?key=' + PUBLIC_CRITINO_API_KEY, '_blank');
		}

		// Update the local submission object to reflect changes
		submission.reasoning = updatedReasoning;
		toast.success('Reasoning updated');
	};
</script>

<div class="flex h-full flex-col">
	{#if submission}
		<div class="flex h-full flex-col gap-y-2">
			<div class="flex flex-row place-items-center justify-between">
				<Typography variant="headline-md" class="p-4 text-left">Post</Typography>
				<Typography variant="title-lg" class="text-left {submission.is_relevant ? 'text-green-600' : 'text-red-600'}">
					{submission.is_relevant ? "Relevant" : "Irrelevant"}
				</Typography>
				<Button
					href={submission.url.includes('http')
						? submission.url
						: 'https://reddit.com/' + submission.url}
					target="_blank"
					variant="default"
					class=""
				>
					Visit Post <ExternalLink class="ml-2 w-5" />
				</Button>
			</div>

			<div class="flex flex-row justify-between p-4 text-left">
				<div>
					<Typography variant="title-md" class="text-left">
						Title: {submission.title}
					</Typography>
					<Typography variant="title-md" class="text-left">
						Posted: {formatDistanceToNowStrict(submission.submission_created_utc, {
							addSuffix: false,
						})} ago, on {format(submission.submission_created_utc, 'dd/MM')}
					</Typography>
					<Typography variant="title-md" class="text-left">
						Author: {submission.author}
					</Typography>
					<Typography variant="title-md" class="text-left">
						Subredit: {submission.subreddit}
					</Typography>
				</div>
			</div>

			<Separator />
			<div class="flex-1 overflow-y-auto whitespace-pre-wrap p-4 text-left text-sm">
				<Typography variant="body-md" class="text-left">{submission.selftext}</Typography>
			</div>

			<Separator />

			<div class="flex flex-row gap-x-2">
				<div class="flex flex-col gap-y-2 justify-between py-2">
					<Button
						onclick={async () => await handleCritiqueClick(submission, true)}
						disabled={critinoLoading}
						size="icon"
						variant="outline"
						class="flex items-center gap-2 text-green-600 border-green-600 hover:bg-green-600/40 hover:text-white"
					>
						{#if critinoLoading}
							<LoaderCircle class="w-5 animate-spin" />
						{:else}
							<ThumbsUp class="w-5" />
						{/if}
					</Button>
					<Button
						onclick={async () => await handleCritiqueClick(submission, false)}
						disabled={critinoLoading}
						size="icon"
						variant="outline"
						class="flex items-center text-red-600 border-red-600 hover:bg-red-600/40 hover:text-white"
					>
						{#if critinoLoading}
							<LoaderCircle class="w-5 animate-spin" />
						{:else}
							<ThumbsDown class="w-5" />
						{/if}
					</Button>
					</div>
				<div class="flex flex-col max-w-3xl">
					<Typography variant="title-md" class="text-left ">Reasoning</Typography>
					<Typography variant="body-md" class="text-left">
						{submission.reasoning}
					</Typography>
				</div>
			</div>

			<Separator />
			

			<Dialog.Root bind:open={showUpdateDialog}>
				<Dialog.Content class="sm:max-w-3xl">
					<Dialog.Header>
						<Dialog.Title>Correct the reasoning</Dialog.Title>
						<Dialog.Description>
							Rewrite the reasoning to be an optimal response.
						</Dialog.Description>
					</Dialog.Header>
					<div class="grid gap-4 py-4">
						<div class="grid gap-2">
							<Textarea
								bind:value={updatedReasoning}
								placeholder="Enter the updated reasoning..."
								class="min-h-[200px]"
							/>
						</div>
					</div>
					<Dialog.Footer>
						<Button variant="outline" onclick={() => showUpdateDialog = false}>
							Cancel
						</Button>
						<Button onclick={handleUpdateReasoning} disabled={critinoLoading}>
							{#if critinoLoading}
								<LoaderCircle class="w-5 animate-spin" />
							{:else}
								Update & Submit
							{/if}
						</Button>
					</Dialog.Footer>
				</Dialog.Content>
			</Dialog.Root>

			<div class="mt-4">
				<ResponseGenerator 
					submission={submission} 
					projectId={submission.project_id}
				/>
			</div>
		</div>
	{:else}
		<div class="p-8 text-center text-muted-foreground">No submission selected</div>
	{/if}
</div>
