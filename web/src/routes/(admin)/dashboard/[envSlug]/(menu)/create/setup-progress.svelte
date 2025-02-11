<script lang="ts">
    import { Check } from 'lucide-svelte';
    import type { SetupStep } from '.';

    export let steps: SetupStep[];
    export let currentStep: number;
</script>

<div class="space-y-4 pb-4">
    <div class="relative after:absolute after:left-[1.125rem] after:top-[1.75rem] after:h-[calc(100%-2rem)] after:w-[2px] after:bg-muted">
        <div class="space-y-4">
            {#each steps as step, index}
                <div class="flex flex-row gap-4">
                    <div class="relative z-10 flex h-9 w-9 items-center justify-center rounded-full border bg-background">
                        {#if step.isComplete}
                            <Check class="h-4 w-4 text-primary" />
                        {:else}
                            <div class="h-2 w-2 rounded-full {index === currentStep ? 'bg-primary' : 'bg-muted'}" />
                        {/if}
                    </div>
                    <div class="flex flex-col">
                        <div class="text-sm font-medium">{step.title}</div>
                        <div class="text-sm text-muted-foreground">{step.description}</div>
                    </div>
                </div>
            {/each}
        </div>
    </div>
</div> 