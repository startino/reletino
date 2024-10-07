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
	import { CheckCheck, ExternalLink, LoaderCircle, Undo } from 'lucide-svelte';
	import { PUBLIC_CRITINO_API_KEY } from '$env/static/public';

	interface Props {
		supabase: SupabaseClient<any, 'public', any>;
		environment: Tables<'environment'>;
		submission: Tables<'submissions'>;
		projectName: string;
	}

	let { supabase, submission = $bindable(), projectName = $bindable() }: Props = $props();

	// Reactive UI
	let critinoLoading = $state(false);
	let markingAsRead = $state(false);

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

	const handleCritique = async (submission: Tables<'submissions'>) => {
		critinoLoading = true;

		const context = '';
		const query = `<title>${submission.title}</title><selftext>${submission.selftext}</selftext>`;
		const response = `{"reasoning": "${submission.reasoning}", "is_relevant": "${submission.is_relevant}"}`;
		const optimal = '';

		const postObject = {
			params: {
				path: { id: submission.id },
				query: {
					team_name: 'startino',
					environment_name: 'reletino/' + $page.data.environment.name + '/' + projectName,
					workflow_name: projectName,
					agent_name: 'main',
				},
				header: {
					'x-critino-key': PUBLIC_CRITINO_API_KEY,
				},
			},
			body: {
				context,
				query,
				optimal,
				response,
			},
		};
		console.log(`Creating Critique with object: ${JSON.stringify(postObject, null, 2)}...`);

		const res = await critino.POST('/critiques/{id}', postObject);

		console.log(`Creating Critique with response: ${JSON.stringify(res, null, 2)}`);

		if (res.data) {
			critinoLoading = false;
			console.log('Opening Critino');
			window.open(res.data.url + '?key=' + $page.data.environment.critino_key, '_blank');
			return;
		}
		if (res.error) {
			console.dir(res);
			console.error(
				`Error:\nMessage: ${res.error.detail?.message}\n${res.error.detail?.traceback}`
			);
			toast.error(`Error sending message: ${res.error.detail?.message}`);
		}
		critinoLoading = false;
	};
</script>

<div class="flex h-full flex-col">
	{#if submission}
		<div class="flex h-full flex-col">
			<div class="flex flex-row place-items-center justify-between">
				<Typography variant="headline-md" class="p-4 text-left">Post</Typography>
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
			<!-- <div class="flex flex-col p-4 self-end">
        <Typography variant="title-lg" class="text-left">
          {submission.is_relevant ? "Relevant" : "Irrelevant"}
        </Typography>
        <Typography variant="title-md" class="text-left">Reasoning</Typography>
        <Typography variant="body-md" class="text-left">
          {submission.reasoning}
        </Typography>
      </div> -->

			<Separator />
			<div class="grid w-full grid-cols-2 gap-6 p-4">
				<Button
					onclick={async () => await handleCritique(submission)}
					variant="secondary"
					target="_blank"
					disabled={critinoLoading}
				>
					Create Critino Review
					{#if critinoLoading}
						<LoaderCircle class="ml-2 w-5 animate-spin" />
					{:else}
						<ExternalLink class="ml-2 w-5" />
					{/if}
				</Button>
				<Button onclick={() => markAsRead()} disabled={markingAsRead}>
					{#if !submission.done}
						Mark as Read
					{:else}
						Mark as Unread
					{/if}
					{#if markingAsRead}
						<LoaderCircle class="ml-2 w-5 animate-spin" />
					{:else if !submission.done}
						<CheckCheck class="ml-2 w-5" />
					{:else}
						<Undo class="ml-2 w-5" />
					{/if}
				</Button>
			</div>
		</div>
	{:else}
		<div class="p-8 text-center text-muted-foreground">No submission selected</div>
	{/if}
</div>
