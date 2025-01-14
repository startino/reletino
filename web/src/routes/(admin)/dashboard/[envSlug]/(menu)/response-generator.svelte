<script lang="ts">
    import { Textarea } from '$lib/components/ui/textarea';
    import { toast } from 'svelte-sonner';
    import type { Tables } from '$lib/supabase';
	import { PUBLIC_API_URL } from '$env/static/public';
    import { Copy, LoaderCircle, ThumbsUp, ThumbsDown } from 'lucide-svelte';
    import { handleCommentOrDmCritique } from '$lib/apis/critino';
    import { page } from '$app/stores';
    import { Button } from '$lib/components/ui/button';

    type Props = {
        submission: Tables<'submissions'>;
        projectId: string;
    }

    let { submission, projectId } = $props();

    let generating = $state(false);
    let generatedResponse = $state('');
    let feedbackLoading = $state(false);

    let updatedResponse = $state('');

    const handleApprove = async () => {
        await handleCommentOrDmCritique(
            submission,
            generatedResponse,
            generatedResponse,
            '', // instructions
            submission.project_name,
            $page.data.environment.name,
            ''
        );
    }

    const handleFeedback = async (isGood: boolean) => {
        feedbackLoading = true;
        const res = await handleCommentOrDmCritique(
            submission,
            generatedResponse,
            updatedResponse,
            '', // instructions
            submission.project_name,
            $page.data.environment.name,
            ''
        );

        feedbackLoading = false;

        if (!res) return;

        toast.success('Feedback submitted');
    }

    async function generateResponse(isDM: boolean) {
        generating = true;
        try {        
            console.log("Generating response with:", {
                project_id: projectId,
                submission_title: submission.title,
                submission_selftext: submission.selftext,
                is_dm: isDM
            });
            const response = await fetch(`${PUBLIC_API_URL}/generate-response`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    project_id: projectId,
                    submission_title: submission.title,
                    submission_selftext: submission.selftext,
                    is_dm: isDM
                })
            });

            if (!response.ok) {
                const text = await response.text();
                console.error("Response not OK:", response.status, text);
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            console.log("Response data:", data);
            
            if (data.status === 'success') {
                generatedResponse = data.response;
                toast.success('Response generated successfully');
            } else {
                toast.error('Failed to generate response', {
                    description: data.message
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

<div class="flex flex-col gap-4">
    <div class="flex gap-2">
        <Button 
            class="w-full" 
            on:click={() => generateResponse(false)} 
            disabled={generating}
        >
            {#if generating}
                <LoaderCircle class="mr-2 h-4 w-4 animate-spin" />
                Generating
            {:else}
                Generate Comment
            {/if}
        </Button>
        <Button 
            class="w-full" 
            on:click={() => generateResponse(true)} 
            disabled={generating}
        >
            {#if generating}
                <LoaderCircle class="mr-2 h-4 w-4 animate-spin" />
                Generating
            {:else}
                Generate DM
            {/if}
        </Button>
    </div>

    {#if generatedResponse}
        <div class="flex flex-col gap-2">
            <div class="flex justify-between items-center">
                <div class="flex flex-row gap-x-4 items-center">
                    <label for="response" class="text-sm font-medium">Generated Response:</label>
                    <Button 
                        variant="outline"
                        size="icon"
                        class="w-fit h-fit p-1"
                        on:click={() => {
                            navigator.clipboard.writeText(generatedResponse);
                            toast.success('Response copied to clipboard');
                        }}
                    >
                        <Copy class="w-4 h-4" />
                    </Button>
                </div>
                <div class="flex gap-2">
                    <Button
                        onclick={() => handleFeedback(true)}
                        disabled={feedbackLoading}
                        size="icon"
                        variant="outline"
                        class="flex items-center gap-2 text-green-600 border-green-600 hover:bg-green-600/40 hover:text-white"
                    >
                        {#if feedbackLoading}
                            <LoaderCircle class="w-4 h-4 animate-spin" />
                        {:else}
                            <ThumbsUp class="w-4 h-4" />
                        {/if}
                    </Button>
                    <Button
                        onclick={() => handleFeedback(false)}
                        disabled={feedbackLoading}
                        size="icon"
                        variant="outline"
                        class="flex items-center text-red-600 border-red-600 hover:bg-red-600/40 hover:text-white"
                    >
                        {#if feedbackLoading}
                            <LoaderCircle class="w-4 h-4 animate-spin" />
                        {:else}
                            <ThumbsDown class="w-4 h-4" />
                        {/if}
                    </Button>
                </div>
            </div>
            <Textarea
                id="response"
                bind:value={generatedResponse}
                rows={6}
                class="w-full"
            />
        </div>
    {/if}
</div>

<style>
    [data-active="true"] {
        background-color: hsl(var(--primary));
        color: hsl(var(--primary-foreground));
    }
</style> 