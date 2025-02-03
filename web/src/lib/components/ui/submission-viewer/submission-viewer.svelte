<script lang="ts">
	import { format, formatDistanceToNowStrict } from 'date-fns';
	import { Button } from '$lib/components/ui/button';
	import { Separator } from '$lib/components/ui/separator';
	import { Textarea } from '$lib/components/ui/textarea';
	import * as Dialog from '$lib/components/ui/dialog';
	import { page } from '$app/stores';

	import type { Tables, Json } from '$lib/supabase';

	import { toast } from 'svelte-sonner';

	import { Typography } from '$lib/components/ui/typography';
	import type { SupabaseClient } from '@supabase/supabase-js';
	import {
		CheckCheck,
		ExternalLink,
		LoaderCircle,
		Undo,
		ThumbsUp,
		ThumbsDown,
		Info,
		Copy,
	} from 'lucide-svelte';
	import ResponseGenerator from './response-generator.svelte';
	import { handleSubmissionCritique } from '$lib/apis/critino';
	import { TipTap } from '$lib/components/ui/tiptap';
	import { ScrollArea } from '$lib/components/ui/scroll-area';
	import { Switch } from '$lib/components/ui/switch';

	type Props = {
		supabase: SupabaseClient<any, 'public', any>;
		submission: Tables<'submissions'>;
		projectName: string;
	};

	let { supabase, submission = $bindable(), projectName = $bindable() }: Props = $props();

	// Reactive UI
	let critinoLoading = $state(false);
	let markingAsRead = $state(false);

	let showUpdateDialog = $state(false);
	let showAuthorDialog = $state(false);

	// Critino variables
	let updatedReasoning = $state('');
	let updatedIsRelevant = $state(false);

	// Function to copy to clipboard so I can easily copy this to my sales
	// management Google Sheet :P
	async function copyToClipboard(submission: Tables<'submissions'>) {
		try {
			const currentDate = new Date();
			// Date has to be MM/DD/YYYY
			const formattedDate = `${currentDate.getMonth() + 1}/${currentDate.getDate()}/${currentDate.getFullYear()}`;
			const cells = [
				submission.author,
				submission.url,
				(submission.approved_dm || '').replace(/\n/g, ' '),
				(submission.approved_comment || '').replace(/\n/g, ' '),
				formattedDate,
			];
			// "	" is the special key that Google sheets uses to separate cells.
			// Select the text to actually see the character since my theme can't see
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

	const handleApprove = async () => {
		critinoLoading = true;
		await handleSubmissionCritique({
			submission,
			projectName,
			teamName: $page.data.environment.name,
			response: submission.reasoning,
			optimal: { reasoning: submission.reasoning, isRelevant: submission.is_relevant },
		});

		const { data, error } = await supabase
			.from('submissions')
			.update({
				approved_evaluation: {
					reasoning: submission.reasoning,
					isRelevant: submission.is_relevant,
				} satisfies Json,
			})
			.eq('id', submission.id)
			.select('*');

		if (error || !data) {
			toast.error('Failed to approve evaluation');
		}

		critinoLoading = false;

		toast.success('Evaluation Critiqued');
	};

	const handleFeedbackButtonClick = () => {
		showUpdateDialog = true;
		updatedReasoning = submission.reasoning;
		updatedIsRelevant = submission.is_relevant;
	};

	const handleFeedback = async () => {
		critinoLoading = true;
		const res = await handleSubmissionCritique({
			submission,
			projectName,
			teamName: $page.data.environment.name,
			response: submission.reasoning,
			optimal: { reasoning: updatedReasoning, isRelevant: updatedIsRelevant },
		});

		if (!res) return;

		const { data, error } = await supabase
			.from('submissions')
			.update({
				approved_evaluation: {
					reasoning: updatedReasoning,
					isRelevant: updatedIsRelevant,
				} satisfies Json,
			})
			.eq('id', submission.id)
			.select('*');

		submission.approved_evaluation = {
			reasoning: updatedReasoning,
			isRelevant: updatedIsRelevant,
		} satisfies Json;

		if (error || !data) {
			toast.error('Failed to update evaluation');
		}

		critinoLoading = false;
		showUpdateDialog = false;

		toast.success('Evaluation Critiqued');
	};
</script>

<div class="flex h-full flex-col">
	{#if submission}
		<div class="flex h-full flex-col gap-y-2">
			<div class="flex flex-row place-items-center justify-between">
				<Typography
					variant="headline-md"
					class="text-left {submission.is_relevant ? 'text-green-600' : 'text-red-600'}"
				>
					{submission.is_relevant ? 'Relevant' : 'Irrelevant'} Post
				</Typography>
				<div class="flex flex-row gap-4">
					<Button
						href={submission.url.includes('http')
							? submission.url
							: 'https://reddit.com/' + submission.url}
						target="_blank"
						variant="default"
						class=""
					>
						Visit <ExternalLink class="ml-2 w-5" />
					</Button>
					<Button onclick={() => markAsRead()} disabled={markingAsRead}>
						{#if !submission.done}
							Read it
						{:else}
							Unread it
						{/if}
						{#if markingAsRead}
							<LoaderCircle class="ml-2 w-5 animate-spin" />
						{:else if !submission.done}
							<CheckCheck class="ml-2 w-5" />
						{:else}
							<Undo class="ml-2 w-5" />
						{/if}
					</Button>
					<Button onclick={() => copyToClipboard(submission)}>
						Copy Lead <Copy class="ml-2 w-5" />
					</Button>
				</div>
			</div>

			<div class="flex flex-row justify-between text-left">
				<div>
					<Typography variant="title-sm" class="text-left">
						<strong>Title:</strong>
						{submission.title}
					</Typography>
					<Typography variant="title-sm" class="text-left">
						<strong>Posted:</strong>
						{formatDistanceToNowStrict(submission.submission_created_utc, {
							addSuffix: false,
						})} ago, on {format(submission.submission_created_utc, 'dd/MM')}
					</Typography>
					<Typography variant="title-sm" class="flex flex-row gap-x-2 text-left">
						<strong>Author:</strong>
						{submission.author}
						<Dialog.Root bind:open={showAuthorDialog}>
							<Button
								onclick={() => (showAuthorDialog = true)}
								variant="ghost"
								class="h-6 w-6"
								size="icon"
							>
								<Info class="w-5" />
							</Button>
							<Dialog.Content class="w-full max-w-3xl">
								<Dialog.Title>Author: {submission.author}</Dialog.Title>
								<Dialog.Description class="w-full max-w-3xl">
									<ScrollArea class="h-[600px] w-full max-w-3xl">
										<TipTap
											editable={false}
											class="text-white"
											content={submission.profile_insights}
										/>
									</ScrollArea>
								</Dialog.Description>
							</Dialog.Content>
						</Dialog.Root>
					</Typography>
					<Typography variant="title-sm" class="text-left">
						<strong>Subreddit:</strong>
						{submission.subreddit}
					</Typography>
				</div>
			</div>

			<Separator />

			<ScrollArea class=" h-[700px] min-h-44 w-full">
				<Typography variant="body-md" class="w-full pr-4 text-left">
					{submission.selftext}
				</Typography>
			</ScrollArea>

			<Separator />

			<div class="flex flex-row gap-x-2">
				<div class="flex flex-col justify-start gap-y-2 pt-2">
					<Button
						onclick={() => handleApprove()}
						disabled={critinoLoading || submission.approved_evaluation}
						size="icon"
						variant="outline"
						class="flex items-center gap-2 border-green-600 text-green-600 hover:bg-green-600/40 hover:text-white"
					>
						{#if critinoLoading}
							<LoaderCircle class="w-5 animate-spin" />
						{:else}
							<ThumbsUp class="w-5" />
						{/if}
					</Button>

					<Button
						size="icon"
						variant="outline"
						class="flex items-center border-red-600 text-red-600 hover:bg-red-600/40 hover:text-white"
						onclick={() => handleFeedbackButtonClick()}
						disabled={critinoLoading || submission.approved_evaluation}
					>
						<ThumbsDown class="w-5" />
					</Button>
				</div>
				<Dialog.Root bind:open={showUpdateDialog}>
					<Dialog.Trigger />
					<Dialog.Content class="sm:max-w-3xl">
						<Dialog.Header>
							<Dialog.Title>Update the Evaluation</Dialog.Title>
							<Dialog.Description>
								What's the final verdict and reasoning?
							</Dialog.Description>
						</Dialog.Header>
						<div class="flex flex-col gap-y-2">
							<div class="flex flex-row items-center gap-4">
								<Typography variant="title-md" class="text-left">
									Final Verdict:
								</Typography>
								<Switch
									bind:checked={updatedIsRelevant}
									aria-label="Toggle relevance"
								>
									<span class="sr-only">Toggle relevance</span>
								</Switch>
								<Typography variant="body-lg" class="text-sm">
									{updatedIsRelevant ? 'Relevant' : 'Irrelevant'}
								</Typography>
							</div>
							<Textarea
								bind:value={updatedReasoning}
								placeholder="Enter the updated reasoning..."
								class="min-h-[300px]"
							/>
						</div>
						<Dialog.Footer>
							<Button variant="outline" onclick={() => (showUpdateDialog = false)}>
								Cancel
							</Button>
							<Button onclick={handleFeedback} disabled={critinoLoading}>
								{#if critinoLoading}
									<LoaderCircle class="w-5 animate-spin" />
								{:else}
									Update & Submit
								{/if}
							</Button>
						</Dialog.Footer>
					</Dialog.Content>
				</Dialog.Root>

				<div class="flex w-full flex-col">
					<Typography variant="title-sm" class="text-left ">Reasoning</Typography>
					<ScrollArea class="max-h-[100px] min-h-24 w-full">
						<Typography variant="body-md" class="text-left">
							{submission.reasoning}
						</Typography>
					</ScrollArea>
				</div>
			</div>
			<Separator />

			<div class="mt-1">
				<ResponseGenerator
					{supabase}
					bind:submission
					projectId={submission.project_id}
					{projectName}
				/>
			</div>
		</div>
	{:else}
		<div class="p-8 text-center text-muted-foreground">No submission selected</div>
	{/if}
</div>
