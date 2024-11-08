<script lang="ts">
	import { Input } from '$lib/components/ui/input';
	import { Button } from '$lib/components/ui/button';
	import { Badge } from '$lib/components/ui/badge';
	import { Plus, X } from 'lucide-svelte';

	type Props = {
		items: string[];
		placeholder?: string;
		onNewItem?: (item: string) => string;
	};

	let value = $state('');

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
	<div class="flex gap-2">
		<Input
			bind:value
			{placeholder}
			onkeydown={(e) => {
				if (e.key === 'Enter') {
					e.preventDefault();
					addItem();
				}
			}}
		/>
		<Button type="button" variant="outline" onclick={addItem}>
			<Plus />
		</Button>
	</div>
	{#if items.length > 0}
		<ul class="flex flex-wrap gap-2">
			{#each items as item, idx}
				<li>
					<Button
						variant="outline"
						class="bg-card hover:bg-destructive/20 flex w-full flex-row justify-between gap-2 rounded-md px-2 py-1 font-semibold"
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
