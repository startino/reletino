<script lang="ts">
    type Step = {
        title: string;
        description: string;
    };

    export let steps: Step[];
    export let currentStep: number;

    $: progress = ((currentStep + 1) / steps.length) * 100;
</script>

<div class="space-y-4">
    <div class="relative h-2 bg-muted rounded-full overflow-hidden">
        <div
            class="absolute h-full bg-primary transition-all duration-300 ease-in-out"
            style="width: {progress}%"
        />
    </div>
    <div class="grid grid-cols-3 gap-4">
        {#each steps as step, index}
            <div class="text-sm {index <= currentStep ? 'text-primary' : 'text-muted-foreground'}">
                <div class="font-medium">{step.title}</div>
                <div class="text-xs">{step.description}</div>
            </div>
        {/each}
    </div>
</div> 