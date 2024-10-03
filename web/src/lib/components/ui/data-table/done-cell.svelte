<script lang="ts">
	import { Check, CircleDashed } from 'lucide-svelte';
	import { Button } from '$lib/components/ui/button';
	import { Input } from '$lib/components/ui/input';
	import { enhance } from '$app/forms';

	export let done: boolean;
</script>

{#key done}
	{#if done}
		<Check size="24" class="text-green-500" />
	{:else}
		<CircleDashed size="24" class="text-orange-500" />
	{/if}
{/key}
