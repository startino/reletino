<script lang="ts">
    import { Button } from '$lib/components/ui/button';
    import { Input } from '$lib/components/ui/input';
    import { Card } from '$lib/components/ui/card';
    import { Alert, AlertDescription } from '$lib/components/ui/alert';
    import { Loader2, Search, AlertCircle, History, Clock, X } from 'lucide-svelte';
    import { PUBLIC_API_URL } from '$env/static/public';
    import { onMount } from 'svelte';

    interface HistoryEntry {
        username: string;
        analysis: string;
        timestamp: number;
    }

    let username = $state('');
    let analysis = $state('');
    let isLoading = $state(false);
    let error = $state('');
    let history = $state<HistoryEntry[]>([]);
    const MAX_HISTORY = 10;

    onMount(() => {
        const savedHistory = localStorage.getItem('profile-analysis-history');
        if (savedHistory) {
            history = JSON.parse(savedHistory);
        }
    });

    function addToHistory(username: string, analysis: string) {
        const newEntry: HistoryEntry = {
            username,
            analysis,
            timestamp: Date.now()
        };
        
        history = [newEntry, ...history.slice(0, MAX_HISTORY - 1)];
        localStorage.setItem('profile-analysis-history', JSON.stringify(history));
    }

    function removeFromHistory(index: number) {
        history = history.filter((_, i) => i !== index);
        localStorage.setItem('profile-analysis-history', JSON.stringify(history));
    }

    function loadFromHistory(entry: HistoryEntry) {
        username = entry.username;
        analysis = entry.analysis;
    }

    const onSubmit = async (event: Event) => {
        if (!username.trim()) {
            error = 'Please enter a username';
            return;
        }

        error = '';
        isLoading = true;
        analysis = '';

        try {
            const response = await fetch(`${PUBLIC_API_URL}/analyze-profile`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    username: username,
                }),
            });

            const data = await response.json();

            if (!response.ok) {
                error = data.message || 'Failed to analyze profile';
            } else {
                analysis = data.analysis;
                addToHistory(username, data.analysis);
            }
        } catch (e) {
            error = 'An unexpected error occurred';
            console.error('API Error:', e);
        } finally {
            isLoading = false;
        }
    }

    function formatDate(timestamp: number): string {
        return new Date(timestamp).toLocaleString();
    }
</script>

<div class="container mx-auto p-4 max-w-[1400px]">
    <div class="grid grid-cols-1 lg:grid-cols-[1fr,400px] gap-8">
        <!-- Main Content Column -->
        <div class="space-y-8">
            <Card class="p-6">
                <h2 class="text-2xl font-bold mb-6">Profile Research</h2>
                
                <form on:submit|preventDefault={onSubmit} class="space-y-4">
                    <div class="flex gap-2">
                        <Input 
                            bind:value={username} 
                            placeholder="Enter username to analyze" 
                            disabled={isLoading}
                            class="flex-1"
                        />
                        <Button type="submit" disabled={isLoading} class="min-w-[120px]">
                            {#if isLoading}
                                <Loader2 class="mr-2 h-4 w-4 animate-spin" />
                                Analyzing
                            {:else}
                                <Search class="mr-2 h-4 w-4" />
                                Analyze
                            {/if}
                        </Button>
                    </div>
                    <p class="text-sm text-muted-foreground flex items-center gap-2">
                        <Clock class="h-4 w-4" />
                        Profile analysis typically takes 1-3 minutes to complete
                    </p>
                </form>

                {#if error}
                    <Alert variant="destructive" class="mt-4">
                        <AlertCircle class="h-4 w-4" />
                        <AlertDescription>{error}</AlertDescription>
                    </Alert>
                {/if}
            </Card>

            {#if analysis}
                <Card class="p-6">
                    <div class="prose dark:prose-invert max-w-none">
                        {@html analysis}
                    </div>
                </Card>
            {/if}
        </div>

        <!-- History Column -->
        <div class="lg:h-[calc(100vh-2rem)] lg:sticky lg:top-4">
            <Card class="p-6 h-full">
                <div class="flex items-center gap-2 mb-4">
                    <History class="h-5 w-5" />
                    <h3 class="text-xl font-semibold">Analysis History</h3>
                </div>
                {#if history.length > 0}
                    <div class="space-y-4 h-[calc(100%-4rem)] overflow-y-auto">
                        {#each history as entry, i}
                            <div class="flex items-start justify-between gap-4 p-3 rounded-lg border hover:bg-muted/50 transition-colors">
                                <div class="flex-1 min-w-0">
                                    <div class="flex items-center gap-2 flex-wrap">
                                        <span class="font-medium truncate">{entry.username}</span>
                                        <span class="text-sm text-muted-foreground flex items-center gap-1 shrink-0">
                                            <Clock class="h-3 w-3" />
                                            {formatDate(entry.timestamp)}
                                        </span>
                                    </div>
                                    <div class="mt-2 line-clamp-2 text-sm text-muted-foreground">
                                        {@html entry.analysis}
                                    </div>
                                </div>
                                <div class="flex gap-2 shrink-0">
                                    <Button 
                                        variant="outline" 
                                        size="sm"
                                        on:click={() => loadFromHistory(entry)}
                                    >
                                        Load
                                    </Button>
                                    <Button 
                                        variant="ghost" 
                                        size="sm"
                                        class="text-destructive hover:text-destructive"
                                        on:click={() => removeFromHistory(i)}
                                    >
                                        <X class="h-4 w-4" />
                                    </Button>
                                </div>
                            </div>
                        {/each}
                    </div>
                {:else}
                    <div class="flex flex-col items-center justify-center h-[calc(100%-4rem)] text-muted-foreground">
                        <History class="h-12 w-12 mb-2 opacity-50" />
                        <p class="text-sm">No analysis history yet</p>
                    </div>
                {/if}
            </Card>
        </div>
    </div>
</div> 