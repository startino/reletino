<script lang="ts">
    import { goto } from '$app/navigation';
    import { Loader2, Plus, X } from 'lucide-svelte';
    import { Button } from '$lib/components/ui/button';
    import { Input } from '$lib/components/ui/input';
    import { Label } from '$lib/components/ui/label';
    import { Card } from '$lib/components/ui/card';
    import { Badge } from '$lib/components/ui/badge';
    import { Textarea } from '$lib/components/ui/textarea';
    import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '$lib/components/ui/select';
    import { RadioGroup, RadioGroupItem } from '$lib/components/ui/radio-group';
    import ProgressBar from './progress-bar.svelte';
    import SetupProgress from './setup-progress.svelte';
    import { generateSubredditsAndPrompt } from './mock-ai-agent';
    import type { ProjectSetup, SetupStep } from '.';
    import { OBJECTIVES } from '.';
    import { TipTap } from '$lib/components/ui/tiptap';
	import { PUBLIC_API_URL } from '$env/static/public';
	import { Typography } from '$lib/components/ui/typography';
	import { getEnvironmentState } from '$lib/states';

    let currentStep = 0;
    let isLoading = false;
    let newSubreddit = '';
    let saasInputType: 'url' | 'text' = 'url';

    const env = getEnvironmentState();

    let projectForm: ProjectSetup = {
        objective: '',
        selectedSubreddits: [],
        filteringPrompt: '',
        saasUrl: '',
        saasDescription: '',
    };

    $: steps = [
        {
            title: 'Basic Details',
            description: 'Name and objective',
            isComplete: !!projectForm.objective,
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
    ] satisfies SetupStep[];

    async function handleNext() {
        if (currentStep === 0) {
            isLoading = true;
            try {
                // Request AI Agent to generate subreddits and filtering prompt
                const data = await fetch(`${PUBLIC_API_URL}/setup-project`, {
                    method: 'POST',
                    body: JSON.stringify({
                        objective: projectForm.objective,
                        ...(saasInputType === 'url' 
                            ? { saasUrl: projectForm.saasUrl }
                            : { saasDescription: projectForm.saasDescription }),
                    }),
                }).then(res => res.json());

                projectForm.selectedSubreddits = data.subreddits;
                projectForm.filteringPrompt = data.filteringPrompt;
                currentStep++;
            } finally {
                isLoading = false;
            }
        }
        if (currentStep < steps.length - 1) {
            currentStep++;
        }
    }

    function handleBack() {
        if (currentStep > 0) {
            currentStep--;
        }
    }

    function handleComplete() {
        goto(`/projects/new-project/edit`);
    }

    function addSubreddit() {
        if (newSubreddit) {
            projectForm.selectedSubreddits = [...projectForm.selectedSubreddits, newSubreddit];
            newSubreddit = '';
        }
    }

    function removeSubreddit(subreddit: string) {
        projectForm.selectedSubreddits = projectForm.selectedSubreddits.filter(s => s !== subreddit);
    }
</script>

<div class="container max-w-3xl py-10">
    <Card class="p-6">
        <ProgressBar {steps} {currentStep} />
        <div class="mt-8 space-y-6">
            {#if currentStep === 0}
                <div class="space-y-8">
                    <div class="flex flex-col gap-2">
                        <Label for="objective">Project Objective</Label>
                        <Select onSelectedChange={(objective) => projectForm.objective = objective?.value as string}>
                            <SelectTrigger>
                                <SelectValue placeholder="Select your objective" />
                            </SelectTrigger>
                            <SelectContent>
                                {#each OBJECTIVES as objective}
                                    <SelectItem value={objective.value}>{objective.label}</SelectItem>
                                {/each}
                            </SelectContent>
                        </Select>
                    </div>
                    <div class="flex flex-col gap-4">
                        <Label>SaaS Information</Label>
                        <RadioGroup bind:value={saasInputType} class="flex gap-4">
                            <div class="flex items-center space-x-2">
                                <RadioGroupItem value="url" id="url" />
                                <Label for="url">Website URL</Label>
                            </div>
                            <div class="flex items-center space-x-2">
                                <RadioGroupItem value="text" id="text" />
                                <Label for="text">Text Description</Label>
                            </div>
                        </RadioGroup>
                        
                        {#if saasInputType === 'url'}
                            <Input
                                id="saasUrl"
                                bind:value={projectForm.saasUrl}
                                placeholder="https://your-saas.com"
                                type="url"
                            />
                        {:else}
                            <Textarea
                                id="saasDescription"
                                bind:value={projectForm.saasDescription}
                                placeholder="Describe your SaaS product..."
                                rows={4}
                            />
                        {/if}
                    </div>
                </div>
            {:else if currentStep === 1}
                <div class="space-y-6">
                    <div>
                        <Label>Subreddits</Label>
                        <p class="text-sm text-muted-foreground mb-2">Edit generated subreddits or add new ones</p>
                        <div class="space-y-3">
                            <div class="flex gap-2">
                                <Input
                                    placeholder="Add a subreddit..."
                                    bind:value={newSubreddit}
                                    on:keydown={(e) => {
                                        if (e.key === 'Enter' && newSubreddit) {
                                            addSubreddit();
                                        }
                                    }}
                                />
                                <Button variant="secondary" onclick={addSubreddit}>
                                    <Plus class="mr-2" /> Add
                                </Button>
                            </div>
                            <div class="flex flex-wrap gap-2">
                                {#each projectForm.selectedSubreddits as subreddit}
                                    <Badge
                                        variant="outline"
                                        class="cursor-pointer hover:bg-destructive/90 hover:text-destructive-foreground"
                                        onclick={() => removeSubreddit(subreddit)}
                                    >
                                        r/{subreddit}
                                        <X class="ml-1 h-3 w-3" />
                                    </Badge>
                                {/each}
                            </div>
                        </div>
                    </div>
                    <div>
                        <Label>Filtering Prompt</Label>
                        <p class="text-sm text-muted-foreground mb-2">
                            Edit the generated prompt to fine-tune your filtering criteria
                        </p>
                        <div class="rounded-lg border">
                            <TipTap
                                bind:content={projectForm.filteringPrompt}
                                class="min-h-[300px] p-4"
                            />
                        </div>
                        <div class="mt-2 text-xs text-muted-foreground">Supports Markdown formatting</div>
                    </div>
                </div>
            {:else if currentStep === 2}
                <div class="space-y-6">
                    <div class="rounded-lg p-4">
                        <h3 class="font-medium">Setup Complete! 🎉</h3>
                        <p class="mt-2 text-sm text-muted-foreground">
                            Your project has been created. You can now configure additional settings:
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
                    <Button onclick={handleComplete}>Go to Project</Button>
                {:else}
                    <Button onclick={handleNext} disabled={currentStep >= steps.length || !steps[currentStep]?.isComplete || isLoading}>
                        {#if isLoading}
                            <Loader2 class="mr-2 h-4 w-4 animate-spin" />
                            Generating...
                        {:else}
                            Next Step
                        {/if}
                    </Button>
                {/if}
            </div>
           
        </div>

    </Card>
    <div class="mt-4 mx-auto w-fit">
        <a href={`/dashboard/${env.value?.slug}`} class="text-sm underline hover:text-primary">
            Back to Projects
        </a>
    </div>
</div> 