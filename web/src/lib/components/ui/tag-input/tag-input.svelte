<script lang="ts">
	import { Button } from '$lib/components/ui/button';
	import { Plus, X } from 'lucide-svelte';

	type Props = {
		items: string[];
		placeholder?: string;
		onNewItem?: (item: string) => string;
	};

	let value = $state('');
	let focus = $state(false);

	let { items = $bindable(), placeholder, onNewItem }: Props = $props();

	$inspect(items);
	const addItem = () => {
		if (value) {
			onNewItem && (value = onNewItem(value));
			items = [...items, value];
			value = '';
		}
	};
</script>

<div class="grid gap-3">
	<div
		class="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm focus-visible:outline-none disabled:cursor-not-allowed disabled:opacity-50 {focus
			? 'ring-2 ring-ring ring-offset-2 ring-offset-background'
			: ''}"
	>
		<input
			class="flex-1 border-none bg-transparent p-0 placeholder:text-muted-foreground focus:border-transparent focus:ring-0"
			onfocus={() => (focus = true)}
			onblur={() => (focus = false)}
			bind:value
			{placeholder}
			onkeydown={(e) => {
				if (e.key === 'Enter') {
					e.preventDefault();
					addItem();
				}
			}}
		/>
		<button type="button" onclick={addItem}>
			<Plus class={value ? '' : 'text-muted-foreground'} />
		</button>
	</div>
	{#if items.length > 0}
		<ul class="flex flex-wrap gap-2">
			{#each items as item, idx}
				<li>
					<Button
						variant="outline"
						class="flex w-full flex-row justify-between gap-2 rounded-md bg-card px-2 py-1 font-semibold hover:bg-destructive/20"
						onclick={() => {
							items = items.filter((_, i) => i !== idx);
						}}
					>
						{item}
						<X size={16} class="text-destructive" />
					</Button>
				</li>
			{/each}
		</ul>
	{/if}
</div>
