<script lang="ts">
	import { fly } from 'svelte/transition';
	import { Menu, ChevronLeft, ChevronRight, Component, Home, Icon, UserSearch, Settings } from 'lucide-svelte';

	import { buttonVariants } from '$lib/components/ui/button';
	import * as Dialog from '$lib/components/ui/dialog';
	import { page } from '$app/stores';
	import { Typography } from '$lib/components/ui/typography';
	import { Separator } from '$lib/components/ui/separator';
	import * as Tooltip from '$lib/components/ui/tooltip';
	import { Info } from 'lucide-svelte';
	import { sub } from 'date-fns';
	import { getEnvironmentState } from '$lib/states/environment.svelte';
	import type { ComponentType } from 'svelte';
	import type { Icon as IconType } from 'lucide-svelte';

	let { data, children } = $props();

	let { session, supabase, usage } = data;

	let open = $state(false);
	let isCollapsed = $state(false);

	const basePath = '/dashboard/';

	const environment = getEnvironmentState();

	let credits = $state(usage ? usage.credits : 69);

	type NavItem = {
		href: string;
		label: string;
		active: boolean;
		icon: typeof IconType;
	};

	let navItems = $state<NavItem[]>([]);

	$effect(() => {
		navItems = [
			{
				href: `${basePath}${environment.value?.slug}`,
				label: 'Projects',
				active: $page.url.pathname === `${basePath}${environment.value?.slug}`,
				icon: Home
			},
			{
				href: `${basePath}${environment.value?.slug}/profile-research`,
				label: 'Redditor Analysis',
				active: $page.url.pathname.startsWith(`${basePath}${environment.value?.slug}/profile-research`),
				icon: UserSearch
			},
			{
				href: `${basePath}${environment.value?.slug}/lead-manager`,
				label: 'Lead Manager',
				active: $page.url.pathname.startsWith(`${basePath}${environment.value?.slug}/lead-manager`),
				icon: Component
			},
		];
	});

	supabase
		.channel('usage')
		.on(
			'postgres_changes',
			{ event: 'UPDATE', schema: 'public', table: 'usage' },
			(payload) => {
				credits = payload.new.credits;
			}
		)
		.subscribe();
</script>

<svelte:head>
	<title>Dashboard</title>
</svelte:head>

<div
	class="grid grid-rows-[auto_1fr] lg:grid-rows-1 lg:grid-cols-[auto_2fr] overflow-hidden top-0 bottom-0 right-0 left-0 absolute bg-background"
>
	<nav
		class="w-full ml-4 my-6 rounded-lg flex flex-col items-center p-4 bg-card text-card-foreground transition-all duration-300"
		class:lg:w-54={!isCollapsed}
		class:lg:w-20={isCollapsed}
	>
		<a href="/" class="text-xl font-bold inline lg:hidden">
			<img src="/favicon.png" class="w-10 h-10" alt="reletino logo" />
		</a>
		<Dialog.Root bind:open>
			<Dialog.Trigger class="lg:hidden">
				<button aria-label="open navigation"><Menu /></button>
			</Dialog.Trigger>
			<Dialog.Content
				transition={(node) => fly(node, { x: 300, duration: 300 })}
				class="left-auto right-0 flex h-dvh max-h-screen w-full max-w-lg translate-x-1 flex-col overflow-y-scroll border-y-0 sm:rounded-none"
			>
				<ul class="flex flex-col">
					{#each navItems as { href, label, active }}
						<li class="my-1">
							<a
								{href}
								class="{buttonVariants({
									variant: active ? 'default' : 'ghost',
								})} w-full"
								onclick={() => (open = false)}
							>
								{label}
							</a>
						</li>
					{/each}
					<span class="flex-grow"></span>
					<li>
						<a
							href="/sign_out"
							class="{buttonVariants({ variant: 'ghost' })} w-full"
							onclick={() => (open = false)}
						>
							Sign Out
						</a>
					</li>
				</ul>
			</Dialog.Content>
		</Dialog.Root>
		<ul class="hidden flex-col h-full lg:flex">
			<li class="mb-6 flex flex-col">
				<a href="/" class="text-xl font-bold flex flex-row place-items-center gap-2" class:hidden={isCollapsed}>
					<img src="/reletino_logo.png" class="w-10 h-10" alt="reletino logo" />
					Reletino
				</a>

			</li>

			{#each navItems as item}
			{@const Icon = item.icon}
				<li class="my-2 w-full">
					{#if isCollapsed}
						<Tooltip.Root>
							<Tooltip.Trigger class="w-full">
								<a
									href={item.href}
									class="{buttonVariants({
										variant: item.active ? 'secondary' : 'ghost',
									})} w-full"
								>
									<span class="truncate w-8">{item.label[0]}</span>
								</a>
							</Tooltip.Trigger>
							<Tooltip.Content side="right">
								<p>{item.label}</p>
							</Tooltip.Content>
						</Tooltip.Root>
					{:else}
						<a
							href={item.href}
							class="w-full text-left flex flex-row place-items-center hover:bg-accent p-2 rounded-md"
						>
							<Icon class="w-4 h-4 mr-2" />
						{item.label}
						</a>
					{/if}
				</li>
			{/each}
			<span class="flex-grow"></span>
			<li class="my-7 w-full">
				<div class="flex flex-col border rounded-md p-2 w-full relative">
					{#if !isCollapsed}
						<Info class="right-2 w-5 absolute" />
					{/if}
					<Typography variant="body-sm" class="font-light pt-2">
						{credits}
					</Typography>
					{#if !isCollapsed}
						<Typography variant="body-sm" class="font-light">
							Credits remaining
						</Typography>
					{/if}
				</div>
			</li>
			<li>
				{#if isCollapsed}
					<a
						href="/sign_out"
						class="{buttonVariants({
							variant: 'ghost',
						})} w-full flex flex-col place-items-center"
					>
						<span class="truncate w-8">Out</span>
					</a>
				{:else}
					<a
						href="/sign_out"
						class="{buttonVariants({
							variant: 'ghost',
						})} w-full flex flex-col place-items-center"
					>
						Sign Out
						<Typography variant="body-sm" class="font-light">
							{session?.user.user_metadata.full_name
								? `(${session?.user.user_metadata.full_name})`
								: ''}
						</Typography>
					</a>
				{/if}
			</li>
		</ul>
	</nav>

	<div class="w-full px-6 px-6 py-3 lg:py-6 overflow-y-scroll relative">
		{#if session?.user.is_anonymous}
			<p
				class="text-sm bg-destructive text-destructive-foreground sticky px-4 py-2 text-center rounded-sm mb-4 md:text-base"
			>
				You're signed in as an anonymous user. <a href="/login/sign_up" class="underline">
					Sign Up to persist your changes
				</a>
			</p>
		{/if}

		{@render children()}
	</div>
</div>
