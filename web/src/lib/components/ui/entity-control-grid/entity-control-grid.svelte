<script lang="ts">
	import * as Card from '$lib/components/ui/card';
	import { ChevronRight, Plus, X, Pen, Trash } from 'lucide-svelte';
	import { TipTap } from '$lib/components/ui/tiptap';
	import * as Dialog from '../dialog';
	import { Button } from '../button';
	import type { Snippet } from 'svelte';

	type Props = {
		name: string;
		entities: T[];
		itemCell?: Snippet<
			[
				T,
				{
					clickEntity: () => void;
					deleteEntity: () => void;
					editEntity: () => void;
				},
			]
		>;
		addCell?: Snippet<[]>;
		oncreate?: () => void;
		onclick?: OnInteract;
		ondelete?: (idx: number) => void;
		onedit?: OnInteract;
	};

	let {
		name,
		entities = $bindable(),
		oncreate,
		ondelete,
		onclick,
		onedit,
		itemCell,
		addCell,
	}: Props = $props();

	let deleteAtIdx: number = $state(-1);
	let deleteOpen = $state(false);

	type T = $$Generic<{ name: string; description: string }>;
	type OnInteract = (entity: T, index?: number) => void;
</script>

<ul
	class="grid w-full grid-cols-[repeat(auto-fit,_minmax(0,_300px))] items-start justify-center gap-4"
>
	{#if oncreate || (!oncreate && addCell)}
		<li class="h-full w-full">
			{#if addCell}
				{@render addCell()}
			{:else}
				<button class="h-full w-full" onclick={oncreate}>
					<Card.Root
						class="duration-400 group h-full w-full text-left transition-all ease-in-out hover:scale-[102%] hover:shadow-lg"
					>
						<Card.Header class="relative h-full min-h-28 gap-2 space-y-0">
							<div
								class="flex h-full w-full flex-col items-center justify-center gap-2"
							>
								{#if name}
									<Card.Title>Create New {name}</Card.Title>
								{/if}
								<Plus
									class="duration-400 size-6 opacity-100 transition-all ease-in-out group-hover:scale-150 group-hover:opacity-100"
								/>
							</div>
						</Card.Header>
					</Card.Root>
				</button>
			{/if}
		</li>
	{/if}
	{#each entities as entity, idx}
		<li>
			{#if itemCell}
				{@render itemCell(entity, {
					clickEntity: () => onclick && onclick(entity),
					deleteEntity: () => {
						deleteOpen = true;
						deleteAtIdx = idx;
					},
					editEntity: () => onedit && onedit(entity),
				})}
			{:else}
				<button onclick={() => onclick && onclick(entity)}>
					<Card.Root
						class="duration-400 group h-full w-full text-left transition-all ease-in-out hover:scale-[102%] hover:shadow-lg"
					>
						<Card.Header class="relative min-h-28 gap-2 space-y-0">
							<Card.Title class="w-full overflow-hidden text-ellipsis pb-1 pr-6">
								{entity.name}
							</Card.Title>
							<Card.Description>
								{#if entity.description}
									<TipTap
										class="text-background-on"
										editable={false}
										content={entity.description}
									></TipTap>
								{/if}
							</Card.Description>
							<ChevronRight
								class="duration-400 absolute right-5 top-5 opacity-50 transition-all ease-in-out group-hover:scale-150 group-hover:opacity-100"
							/>

							{#if ondelete}
								<div
									role="button"
									tabindex="0"
									class="duration-400 absolute bottom-5 right-5 scale-100 cursor-pointer text-error opacity-60 transition-all ease-in-out hover:scale-150 hover:opacity-100"
									onclick={(event) => {
										event.stopPropagation();
										deleteOpen = true;
										deleteAtIdx = idx;
									}}
									onkeydown={(event) => {
										if (event.key === 'Enter' || event.key === ' ') {
											event.preventDefault();
											event.stopPropagation();
											deleteOpen = true;
											deleteAtIdx = idx;
										}
									}}
								>
									<Trash
										class="scale-0 opacity-0 group-hover:scale-100 group-hover:opacity-100"
									/>
								</div>
							{/if}

							{#if onedit}
								<div
									role="button"
									tabindex="0"
									class="duration-400 absolute bottom-5 right-14 scale-100 cursor-pointer opacity-60 transition-all ease-in-out hover:scale-150 hover:opacity-100"
									onclick={(event) => {
										event.stopPropagation();
										onedit(entity);
									}}
									onkeydown={(event) => {
										if (event.key === 'Enter' || event.key === ' ') {
											event.preventDefault();
											event.stopPropagation();
											onedit(entity);
										}
									}}
								>
									<Pen
										class="scale-0 opacity-0 group-hover:scale-100 group-hover:opacity-100"
									/>
								</div>
							{/if}
						</Card.Header>
					</Card.Root>
				</button>
			{/if}
		</li>
	{/each}
</ul>

<Dialog.Root bind:open={deleteOpen}>
	<Dialog.Trigger />
	<Dialog.Content>
		<Dialog.Header class="gap-2 text-destructive">
			<Dialog.Title>
				Delete {entities[deleteAtIdx]!.name}?
			</Dialog.Title>
			<Dialog.Description>
				<strong>{entities[deleteAtIdx]!.name}</strong>
				will be deleted and unrecoverable.
			</Dialog.Description>
		</Dialog.Header>
		<div class="ml-auto flex gap-2">
			<Button
				variant="destructive"
				on:click={() => {
					entities;
					ondelete && ondelete(deleteAtIdx);
					deleteOpen = false;
				}}
			>
				Delete
			</Button>
			<Button
				on:click={() => {
					deleteOpen = false;
				}}
			>
				Cancel
			</Button>
		</div>
	</Dialog.Content>
</Dialog.Root>
