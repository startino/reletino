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
	import { CheckCheck, ExternalLink, LoaderCircle, Undo, ThumbsUp, ThumbsDown, Info } from 'lucide-svelte';
	import { PUBLIC_CRITINO_API_KEY, PUBLIC_OPENROUTER_API_KEY } from '$env/static/public';
	import ResponseGenerator from './response-generator.svelte';
	import { handleSubmissionCritique } from '$lib/apis/critino';
	import { TipTap } from '$lib/components/ui/tiptap';
	import { ScrollArea } from '$lib/components/ui/scroll-area';
	import { Toggle } from '$lib/components/ui/toggle';
	import { Switch } from '$lib/components/ui/switch';

	type Props = {
		supabase: SupabaseClient<any, 'public', any>;
		submission: Tables<'submissions'>;
		projectName: string;
	}

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

	const handleApprove = async () => {
		critinoLoading = true;
		const res = await handleSubmissionCritique({
			submission,
			projectName,
			teamName: $page.data.environment.name,
			response: submission.reasoning,
			optimal: {reasoning: submission.reasoning, isRelevant: submission.is_relevant},
		});

		critinoLoading = false;

		if (!res) return;
	};

	const handleFeedbackButtonClick = () => {
		showUpdateDialog = true;
		updatedReasoning = submission.reasoning;
		updatedIsRelevant = submission.is_relevant;
	}

	const handleFeedback = async () => {
		critinoLoading = true;
		const res = await handleSubmissionCritique({
			submission,
			projectName,
			teamName: $page.data.environment.name,
			response: submission.reasoning,
			optimal: {reasoning: updatedReasoning, isRelevant: updatedIsRelevant},
		});

		critinoLoading = false;
		if (!res) return;

		showUpdateDialog = false;
		toast.success('Reasoning updated');
	}
</script>

<div class="flex h-full flex-col">
	{#if submission}
		<div class="flex h-full flex-col gap-y-2">
			<div class="flex flex-row place-items-center justify-between">
				<Typography variant="headline-md" class="text-left {submission.is_relevant ? 'text-green-600' : 'text-red-600'}">
					{submission.is_relevant ? "Relevant" : "Irrelevant"} Post
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

			<div class="flex flex-row justify-between text-left">
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
						<Dialog.Root bind:open={showAuthorDialog}>
								<Button onclick={() => showAuthorDialog = true} variant="outline" size="icon">
									<Info class="w-5" />
								</Button>
							<Dialog.Content class="max-w-3xl w-full">
								<Dialog.Title>Author: {submission.author}</Dialog.Title>
								<Dialog.Description class="max-w-3xl w-full">
									<ScrollArea class="max-w-3xl w-full h-[600px]">
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
					<Typography variant="title-md" class="text-left">
						Subredit: {submission.subreddit}
					</Typography>
				</div>
			</div>

			<Separator />

				<ScrollArea class="max-w-3xl w-full h-[700px]">
					<Typography variant="body-md" class="text-left">{submission.selftext}</Typography>
				</ScrollArea>
		

			<Separator />

			<div class="flex flex-row gap-x-2">
				<div class="flex flex-col gap-y-2 pt-2 justify-start">
					<Button
						onclick={() => handleApprove()}
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
						size="icon"
						variant="outline"
						class="flex items-center text-red-600 border-red-600 hover:bg-red-600/40 hover:text-white"
						onclick={() => handleFeedbackButtonClick()}
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
							<div class="flex items-center flex-row gap-4">
								<Typography variant="title-md" class="text-left">Final Verdict:</Typography>
								<Switch
									bind:checked={updatedIsRelevant}
									aria-label="Toggle relevance"
								>
									<span class="sr-only">Toggle relevance</span>
								</Switch>
								<Typography variant="body-lg" class="text-sm">{updatedIsRelevant ? "Relevant" : "Irrelevant"}</Typography>
							</div>
							<Textarea
								bind:value={updatedReasoning}
								placeholder="Enter the updated reasoning..."
								class="min-h-[300px]"
							/>
						</div>
					<Dialog.Footer>
						<Button variant="outline" onclick={() => showUpdateDialog = false}>
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


				<div class="flex flex-col max-w-3xl">
					<Typography variant="title-md" class="text-left ">Reasoning</Typography>
					<ScrollArea class="max-w-3xl w-full h-[200px]">
						<Typography variant="body-md" class="text-left">
							{submission.reasoning}
						</Typography>
					</ScrollArea>
				</div>
			</div>
			<Separator />

			<div class="mt-2">
				<ResponseGenerator
					submission={submission} 
					projectId={submission.project_id}
					{projectName}
				/>
			</div>
		</div>
	{:else}
		<div class="p-8 text-center text-muted-foreground">No submission selected</div>
	{/if}
</div>
