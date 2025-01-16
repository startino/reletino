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
    import * as Tabs from '$lib/components/ui/tabs';

    type Props = {
        supabase: SupabaseClient<any, 'public', any>;
        submission: Tables<'submissions'>;
        projectId: string;
        projectName: string;
    }

    let { submission = $bindable(), projectId, projectName, supabase }: Props = $props();

    let generating = $state(false);
    let commentResponse = $state(submission.approved_comment || '');
    let dmResponse = $state(submission.approved_dm || '');
    let feedbackLoading = $state(false);
    let currentTab = $state<'comment' | 'dm'>('comment');

    const handleApprove = async () => {
        const response = currentTab === 'comment' ? commentResponse : dmResponse;
        const isDm = currentTab === 'dm';

        await handleCommentOrDmCritique(
            {
                submission,
                response: response,
                optimal: response,
                projectName: projectName,
                teamName: $page.data.environment.name,
                isDm: isDm
            }
        );

        const {data, error} = await supabase.from('submissions').update(
            {
                approved_dm: isDm ? response : submission.approved_dm,
                approved_comment: !isDm ? response : submission.approved_comment,
            }
        ).eq('id', submission.id).select('*');

        if (error || !data) {
            toast.error('Failed to approve evaluation');
            return;
        }

        if (isDm) {
            submission.approved_dm = response;
        } else {
            submission.approved_comment = response;
        }

        toast.success('Response approved');
    }

    async function generateResponse(isDm: boolean) {
        generating = true;
        try {        
            console.log("Generating response with:", {
                project_id: projectId,
                submission_title: submission.title,
                submission_selftext: submission.selftext,
                is_dm: isDm
            });
            const res = await fetch(`${PUBLIC_API_URL}/generate-response`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    project_id: projectId,
                    submission_title: submission.title,
                    submission_selftext: submission.selftext,
                    team_name: $page.data.environment.name,
                    is_dm: isDm
                })
            });

            if (!res.ok) {
                const text = await res.text();
                console.error("Response not OK:", res.status, text);
                throw new Error(`HTTP error! status: ${res.status}`);
            }

            const data = await res.json();
            console.log("Response data:", data);
            
            if (data.status === 'success') {
                if (isDm) {
                    dmResponse = data.response;
                } else {
                    commentResponse = data.response;
                }
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
    <Tabs.Root value={currentTab} onValueChange={(value) => currentTab = value as 'comment' | 'dm'} class="w-full">
        <Tabs.List class="grid grid-cols-2">
            <Tabs.Trigger value="comment">Comment</Tabs.Trigger>
            <Tabs.Trigger value="dm">Direct Message</Tabs.Trigger>
        </Tabs.List>
        <Tabs.Content value="comment" class="mt-4">
            <div class="flex flex-col gap-4">
                <Button
                    class="w-full" 
                    disabled={generating}
                    on:click={() => generateResponse(false)} 
                >
                    {#if generating}
                        <LoaderCircle class="mr-2 h-4 w-4 animate-spin" />
                        Generating
                    {:else}
                        Generate Comment
                    {/if}
                </Button>

                    <div class="flex flex-col gap-2">
                        <div class="flex justify-between items-center">
                            <div class="flex flex-row gap-x-4 items-center">
                                <label for="comment-response" class="text-sm font-medium">Generated Comment:</label>
                                <Button 
                                    variant="outline"
                                    size="icon"
                                    class="w-fit h-fit p-1"
                                    on:click={() => {
                                        navigator.clipboard.writeText(commentResponse);
                                        toast.success('Response copied to clipboard');
                                    }}
                                >
                                    <Copy class="w-4 h-4" />
                                </Button>
                            </div>
                            <div class="flex gap-2">
                                <Button
                                    on:click={() => handleApprove()}
                                    disabled={feedbackLoading || submission.approved_comment}
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
                            </div>
                        </div>
                        {submission.approved_comment}
                        <Textarea
                            id="comment-response"
                            bind:value={commentResponse}
                            rows={6}
                            disabled={submission.approved_comment}
                            class="w-full"
                        />
                    </div>
            </div>
        </Tabs.Content>
        <Tabs.Content value="dm" class="mt-4">
            <div class="flex flex-col gap-4">
                <Button
                    class="w-full" 
                    disabled={generating}
                    on:click={() => generateResponse(true)} 
                >
                    {#if generating}
                        <LoaderCircle class="mr-2 h-4 w-4 animate-spin" />
                        Generating
                    {:else}
                        Generate DM
                    {/if}
                </Button>

                    <div class="flex flex-col gap-2">
                        <div class="flex justify-between items-center">
                            <div class="flex flex-row gap-x-4 items-center">
                                <label for="dm-response" class="text-sm font-medium">Generated DM:</label>
                                <Button 
                                    variant="outline"
                                    size="icon"
                                    class="w-fit h-fit p-1"
                                    on:click={() => {
                                        navigator.clipboard.writeText(dmResponse);
                                        toast.success('Response copied to clipboard');
                                    }}
                                >
                                    <Copy class="w-4 h-4" />
                                </Button>
                            </div>
                            <div class="flex gap-2">
                                <Button
                                    on:click={() => handleApprove()}
                                    disabled={feedbackLoading || submission.approved_dm}
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
                            </div>
                        </div>
                        <Textarea
                            id="dm-response"
                            bind:value={dmResponse}
                            disabled={submission.approved_dm}
                            rows={8}
                            class="w-full"
                    />
                </div>
            </div>
        </Tabs.Content>
    </Tabs.Root>
</div>