<script lang="ts">
	import { goto } from '$app/navigation';
	import { Loader2, Plus, X } from 'lucide-svelte';
	import { Button } from '$lib/components/ui/button';
	import { Input } from '$lib/components/ui/input';
	import { Label } from '$lib/components/ui/label';
	import { Card } from '$lib/components/ui/card';
	import { Badge } from '$lib/components/ui/badge';
	import { Textarea } from '$lib/components/ui/textarea';
	import {
		Select,
		SelectContent,
		SelectItem,
		SelectTrigger,
		SelectValue,
	} from '$lib/components/ui/select';
	import { RadioGroup, RadioGroupItem } from '$lib/components/ui/radio-group';
	import { TagInput } from '$lib/components/ui/tag-input';
	import ProgressBar from './progress-bar.svelte';
	import { generateSubredditsAndPrompt } from './mock-ai-agent';
	import type { ProjectSetup, SetupStep } from '.';
	import { OBJECTIVES } from '.';
	import { TipTap } from '$lib/components/ui/tiptap';
	import { PUBLIC_API_URL } from '$env/static/public';
	import { Typography } from '$lib/components/ui/typography';
	import { getEnvironmentState } from '$lib/states';
	import {
		Target,
		Users,
		Lightbulb,
		Search,
		DollarSign,
		Handshake,
		Globe,
		FileText,
	} from 'lucide-svelte';
	import type { SupabaseClient, Session } from '@supabase/supabase-js';
	import { toast } from 'svelte-sonner';

	type Props = {
		supabase: SupabaseClient<any, 'public', any>;
		session: Session;
	};

	let { supabase, session }: Props = $props();

	let currentStep = $state(0);
	let isLoading = $state(false);
	let isValidatingSubreddit = $state(false);
	let newSubreddit = $state('');
	let saasInputType = $state<'url' | 'text'>('url');

	const env = getEnvironmentState();

	const objectives = [
		{
			icon: Target,
			label: 'Find Leads',
			value: 'find_leads',
			description: 'Monitor Reddit for potential customers and generate leads',
		},
		{
			icon: Users,
			label: 'Find Competitors',
			value: 'find_competitors',
			description: 'Track competitor mentions and analyze market trends',
		},
		{
			icon: Lightbulb,
			label: 'Find Ideas',
			value: 'find_ideas',
			description: 'Discover new product ideas and market opportunities',
		},
		{
			icon: Search,
			label: 'Find Influencers',
			value: 'find_influencers',
			description: 'Identify and connect with industry influencers',
		},
		{
			icon: DollarSign,
			label: 'Find Investors',
			value: 'find_investors',
			description: 'Locate potential investors and funding opportunities',
		},
		{
			icon: Handshake,
			label: 'Find Partners',
			value: 'find_partners',
			description: 'Discover potential business partners and collaborators',
		},
	];

	const inputMethods = [
		{
			icon: Globe,
			label: 'Website URL',
			value: 'url' as const,
			description: 'I have a website URL',
		},
		{
			icon: FileText,
			label: 'Product Description',
			value: 'text' as const,
			description: 'I want to describe my product',
		},
	];

	const modes = [
		{
			icon: Lightbulb,
			label: 'Standard Mode',
			value: 'standard' as const,
			description: 'Faster but lower quality',
		},
		{
			icon: Target,
			label: 'Advanced Mode',
			value: 'advanced' as const,
			description: 'Higher quality results but slower',
		},
	];

	let projectForm = $state<ProjectSetup>({
		objective: '',
		selectedSubreddits: [],
		filteringPrompt: '',
		projectName: '',
		saasUrl: '',
		saasDescription: '',
		mode: 'advanced' as const,
	});

	const processUrl = (url: string) => {
		if (!url) return '';
		// Remove any whitespace
		url = url.trim();
		// Add https:// if no protocol is specified
		if (!url.startsWith('http://') && !url.startsWith('https://')) {
			url = 'https://' + url;
		}
		return url;
	};

	const steps = $derived([
		{
			title: 'Choose Objective',
			description: 'Select your goal',
			isComplete: !!projectForm.objective,
		},
		{
			title: 'Enter Details',
			description: 'Provide information',
			isComplete:
				saasInputType === 'url' ? !!projectForm.saasUrl : !!projectForm.saasDescription,
		},
		{
			title: 'AI Generation',
			description: 'Generate content',
			isComplete: projectForm.selectedSubreddits.length > 0 && !!projectForm.filteringPrompt,
		},
		{
			title: 'Review',
			description: 'Finish setup',
			isComplete: true,
		},
	] satisfies SetupStep[]);

	const handleNext = async () => {
		if (currentStep === 1) {
			isLoading = true;
			try {
				// Request AI Agent to generate subreddits and filtering prompt
				const data = await fetch(`${PUBLIC_API_URL}/setup-project`, {
					method: 'POST',
					headers: {
						'Content-Type': 'application/json',
					},
					body: JSON.stringify({
						objective: projectForm.objective,
						...(saasInputType === 'url'
							? { url: projectForm.saasUrl }
							: { description: projectForm.saasDescription }),
						mode: projectForm.mode,
					}),
				}).then((res) => res.json());

				projectForm.selectedSubreddits = data.subreddits;
				projectForm.filteringPrompt = data.filtering_prompt;
				projectForm.projectName = data.project_name;

				currentStep++;
			} finally {
				isLoading = false;
			}
			return;
		}

		// Only proceed to review step if we're on AI Generation step (step 2) and there are subreddits and a filtering prompt
		if (
			currentStep === 2 &&
			projectForm.selectedSubreddits.length > 0 &&
			projectForm.filteringPrompt
		) {
			currentStep++;
			return;
		}

		// For other steps, just increment if not at the end
		if (currentStep < steps.length - 1 && currentStep !== 1 && currentStep !== 2) {
			currentStep++;
		}
	};

	const handleBack = () => {
		if (currentStep > 0) {
			currentStep--;
		}
	};

	const handleComplete = async () => {
		console.log('handleComplete');
		isLoading = true;
		const { data, error } = await supabase
			.from('projects')
			.insert({
				profile_id: session.user!.id,
				title: projectForm.projectName,
				context: projectForm.filteringPrompt,
				website_url: projectForm.saasUrl,
				running: true,
				subreddits: projectForm.selectedSubreddits,
				prompt: projectForm.filteringPrompt,
			})
			.select()
			.single();

		if (error) {
			console.error(error);
		}
		// Start the project
		const response = await fetch(`${PUBLIC_API_URL}/start`, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
			},
			body: JSON.stringify({
				project: {
					id: data.id,
					title: data.title,
					profile_id: session.user!.id,
					prompt: projectForm.filteringPrompt,
					subreddits: projectForm.selectedSubreddits,
					running: true,
				},
				team_name: env.value?.name,
			}),
		});

		if (response.ok) {
			goto(`/dashboard/${env.value?.slug}/${data.id}/edit`);
		} else {
			toast.error('Failed to start project');
		}
	};

	const validateSubreddit = async (subreddit: string): Promise<boolean> => {
		isValidatingSubreddit = true;
		try {
			const response = await fetch(`https://www.reddit.com/r/${subreddit}/about.json`);
			const data = await response.json();

			if (response.ok && !data.error) {
				return true;
			} else {
				toast.error(`Subreddit r/${subreddit} does not exist`);
				return false;
			}
		} catch (error) {
			console.error('Error validating subreddit:', error);
			toast.error('Failed to validate subreddit');
			return false;
		} finally {
			isValidatingSubreddit = false;
		}
	};

	const handleNewSubreddit = async (subreddit: string) => {
		const cleanSubreddit = subreddit.toLowerCase().trim().replace('r/', '');
		if (cleanSubreddit && (await validateSubreddit(cleanSubreddit))) {
			return cleanSubreddit;
		}
		return null;
	};
</script>

<div class="w-full max-w-4xl py-10">
	<Card class="p-6">
		<ProgressBar {steps} {currentStep} />
		<div class="mt-8 space-y-6">
			{#if currentStep === 0}
				<div class="space-y-8">
					<div class="flex flex-col gap-2">
						<Typography variant="headline-md" class="mb-1">
							Choose your project's main objective
						</Typography>
						<Typography variant="body-md" class="mb-4">
							Select the primary goal for your Reddit monitoring project
						</Typography>

						<div class="grid grid-cols-1 gap-4 md:grid-cols-2">
							{#each objectives as objective}
								<button
									class="flex flex-col gap-2 rounded-lg border-2 p-6 text-left transition-all hover:border-primary
                                        {projectForm.objective === objective.value
										? 'border-primary bg-primary/5'
										: 'border-border'}"
									onclick={() => (projectForm.objective = objective.value)}
								>
									<div class="flex items-center gap-3">
										<svelte:component this={objective.icon} class="h-5 w-5" />
										<span class="font-medium">{objective.label}</span>
									</div>
									<p class="text-sm text-muted-foreground">
										{objective.description}
									</p>
								</button>
							{/each}
						</div>
					</div>
				</div>
			{:else if currentStep === 1}
				<div class="space-y-8">
					<div class="flex flex-col gap-2">
						<Typography variant="headline-md" class="mb-1">
							Enter your project details
						</Typography>
						<Typography variant="body-md" class="mb-4">
							Provide information about your product or service
						</Typography>

						<div class="mb-6 grid grid-cols-1 gap-4 md:grid-cols-2">
							{#each inputMethods as method}
								<button
									class="flex flex-col gap-2 rounded-lg border-2 p-6 text-left transition-all hover:border-primary
                                        {saasInputType === method.value
										? 'border-primary bg-primary/5'
										: 'border-border'}"
									onclick={() => (saasInputType = method.value)}
								>
									<div class="flex items-center gap-3">
										<svelte:component this={method.icon} class="h-5 w-5" />
										<span class="font-medium">{method.label}</span>
									</div>
									<p class="text-sm text-muted-foreground">
										{method.description}
									</p>
								</button>
							{/each}
						</div>

						{#if saasInputType === 'url'}
							<Input
								id="saasUrl"
								bind:value={projectForm.saasUrl}
								placeholder="your-saas.com"
								type="text"
								on:blur={(e) => {
									projectForm.saasUrl = processUrl(e.currentTarget.value);
								}}
							/>
						{:else if saasInputType === 'text'}
							<Textarea
								id="saasDescription"
								bind:value={projectForm.saasDescription}
								placeholder="Describe your SaaS product..."
								rows={4}
							/>
						{/if}
					</div>
				</div>

				<div class="space-y-8">
					<div class="flex flex-col gap-2">
						<Typography variant="headline-md" class="mb-1">
							Choose processing mode
						</Typography>
						<Typography variant="body-md" class="mb-4">
							Select how you want your project to be processed
						</Typography>

						<div class="grid grid-cols-1 gap-4 md:grid-cols-2">
							{#each modes as mode}
								<button
									class="flex flex-col gap-2 rounded-lg border-2 p-6 text-left transition-all hover:border-primary
                                        {projectForm.mode === mode.value
										? 'border-primary bg-primary/5'
										: 'border-border'}"
									onclick={() => (projectForm.mode = mode.value)}
								>
									<div class="flex items-center gap-3">
										<svelte:component this={mode.icon} class="h-5 w-5" />
										<span class="font-medium">{mode.label}</span>
									</div>
									<p class="text-sm text-muted-foreground">{mode.description}</p>
								</button>
							{/each}
						</div>
					</div>
				</div>
			{:else if currentStep === 2}
				<div class="space-y-6">
					<div>
						<Label>Subreddits</Label>
						<p class="mb-2 text-sm text-muted-foreground">
							Edit generated subreddits or add new ones
						</p>
						<div class="space-y-3">
							<TagInput
								bind:items={projectForm.selectedSubreddits}
								placeholder="Add a subreddit..."
								disabled={isValidatingSubreddit}
								onNewItem={handleNewSubreddit}
							/>
						</div>
					</div>
					<div>
						<Label>Filtering Prompt</Label>
						<p class="mb-2 text-sm text-muted-foreground">
							Edit the generated prompt to fine-tune your filtering criteria
						</p>
						<div class="rounded-lg border">
							<TipTap
								bind:content={projectForm.filteringPrompt}
								class="bg-background-variant min-h-[300px] p-4"
							/>
						</div>
						<div class="mt-2 text-xs text-muted-foreground">
							Supports Markdown formatting
						</div>
					</div>
				</div>
			{:else if currentStep === 3}
				<div class="space-y-6">
					<div class="rounded-lg p-4">
						<h3 class="font-medium">Setup Complete! 🎉</h3>
						<p class="mt-2 text-sm">
							Your project has been created. You can now configure additional
							settings:
						</p>
						<ul class="mt-4 space-y-2 text-sm">
							<li>• Comment Style Prompt</li>
							<li>• DM Style Prompt</li>
						</ul>
					</div>
				</div>
			{/if}

			<div class="flex justify-between pt-4">
				<Button variant="outline" onclick={handleBack} disabled={currentStep === 0}>
					Back
				</Button>
				{#if currentStep === steps.length - 1}
					<Button
						onclick={() => {
							handleComplete();
						}}
					>
						Go to Project
					</Button>
				{:else}
					<div class="flex flex-col gap-2">
						<Button
							onclick={handleNext}
							disabled={currentStep >= steps.length ||
								!steps[currentStep]?.isComplete ||
								isLoading}
						>
							{#if isLoading}
								<Loader2 class="mr-2 h-4 w-4 animate-spin" />
								Generating...
							{:else}
								Next Step
							{/if}
						</Button>
						{#if isLoading}
							<Typography variant="body-sm" class="text-left">
								{projectForm.mode === 'standard'
									? 'This may take up to a minute'
									: 'This may take up to 3 minutes'}
							</Typography>
						{/if}
					</div>
				{/if}
			</div>
		</div>
	</Card>
	<div class="mx-auto mt-4 w-fit">
		<a href={`/dashboard/${env.value?.slug}`} class="text-sm underline hover:text-primary">
			Back to Projects
		</a>
	</div>
</div>
