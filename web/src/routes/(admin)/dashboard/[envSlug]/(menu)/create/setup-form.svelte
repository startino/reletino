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
    import { Target, Users, Lightbulb, Search, DollarSign, Handshake, Globe, FileText } from 'lucide-svelte';

    let currentStep = 0;
    let isLoading = false;
    let newSubreddit = '';
    let saasInputType: 'url' | 'text' = 'url';

    const env = getEnvironmentState();

    const objectives = [
        {
            icon: Target,
            label: 'Find Leads',
            value: 'find_leads',
            description: 'Monitor Reddit for potential customers and generate leads'
        },
        {
            icon: Users,
            label: 'Find Competitors',
            value: 'find_competitors',
            description: 'Track competitor mentions and analyze market trends'
        },
        {
            icon: Lightbulb,
            label: 'Find Ideas',
            value: 'find_ideas',
            description: 'Discover new product ideas and market opportunities'
        },
        {
            icon: Search,
            label: 'Find Influencers',
            value: 'find_influencers',
            description: 'Identify and connect with industry influencers'
        },
        {
            icon: DollarSign,
            label: 'Find Investors',
            value: 'find_investors',
            description: 'Locate potential investors and funding opportunities'
        },
        {
            icon: Handshake,
            label: 'Find Partners',
            value: 'find_partners',
            description: 'Discover potential business partners and collaborators'
        }
    ];

    const inputMethods = [
        {
            icon: Globe,
            label: 'Website URL',
            value: 'url' as const,
            description: 'I have a website URL'
        },
        {
            icon: FileText,
            label: 'Product Description',
            value: 'text' as const,
            description: 'I want to describe my product'
        }
    ];

    let projectForm: ProjectSetup = {
        objective: '',
        selectedSubreddits: [],
        filteringPrompt: '',
        saasUrl: '',
        saasDescription: '',
    };

    $: steps = [
        {
            title: 'Choose Objective',
            description: 'Select your goal',
            isComplete: !!projectForm.objective,
        },
        {
            title: 'Enter Details',
            description: 'Provide information',
            isComplete: saasInputType === 'url' ? !!projectForm.saasUrl : !!projectForm.saasDescription,
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
                        <Typography variant="headline-md" class="mb-1">Choose your project's main objective</Typography>
                        <Typography variant="body-md" class="mb-4">Select the primary goal for your Reddit monitoring project</Typography>
                        
                        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                            {#each objectives as objective}
                                <button
                                    class="flex flex-col gap-2 p-6 rounded-lg border-2 transition-all hover:border-primary text-left
                                        {projectForm.objective === objective.value ? 'border-primary bg-primary/5' : 'border-border'}"
                                    on:click={() => projectForm.objective = objective.value}
                                >
                                    <div class="flex items-center gap-3">
                                        <svelte:component this={objective.icon} class="w-5 h-5" />
                                        <span class="font-medium">{objective.label}</span>
                                    </div>
                                    <p class="text-sm text-muted-foreground">{objective.description}</p>
                                </button>
                            {/each}
                        </div>
                    </div>
                </div>
            {:else if currentStep === 1}
                <div class="space-y-8">
                    <div class="flex flex-col gap-2">
                        <Typography variant="headline-md" class="mb-1">Enter your project details</Typography>
                        <Typography variant="body-md" class="mb-4">Provide information about your product or service</Typography>

                        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                            {#each inputMethods as method}
                                <button
                                    class="flex flex-col gap-2 p-6 rounded-lg border-2 transition-all hover:border-primary text-left
                                        {saasInputType === method.value ? 'border-primary bg-primary/5' : 'border-border'}"
                                    on:click={() => saasInputType = method.value}
                                >
                                    <div class="flex items-center gap-3">
                                        <svelte:component this={method.icon} class="w-5 h-5" />
                                        <span class="font-medium">{method.label}</span>
                                    </div>
                                    <p class="text-sm text-muted-foreground">{method.description}</p>
                                </button>
                            {/each}
                        </div>

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
            {:else if currentStep === 2}
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
            {:else if currentStep === 3}
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