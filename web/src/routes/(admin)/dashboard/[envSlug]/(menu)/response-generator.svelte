<script lang="ts">
    import { Button } from '$lib/components/ui/button';
    import { Textarea } from '$lib/components/ui/textarea';
    import { toast } from 'svelte-sonner';
    import type { Tables } from '$lib/supabase';
	import { PUBLIC_API_URL } from '$env/static/public';
    import { Copy, LoaderCircle } from 'lucide-svelte';

    type Props = {
        submission: Tables<'submissions'>;
        projectId: string;
    }

    let { submission, projectId } = $props();

    let generating = $state(false);
    let generatedResponse = $state('');

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
        <div class="flex flex-col">
            <div class="flex flex-row gap-x-4">
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