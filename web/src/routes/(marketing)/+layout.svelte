<script lang="ts">
	import { Menu } from 'lucide-svelte';
	import { Button, buttonVariants } from '$lib/components/ui/button';
	import * as DropDownMenu from '$lib/components/ui/dropdown-menu';
	import { getEnvironmentState, getAuthState } from '$lib/states';

	import { WebsiteName } from '$lib/config';

	let { children } = $props();
	const environment = getEnvironmentState();
	const authState = getAuthState();
</script>

<div class="h-dvh relative">
	<div
		class="flex w-full place-content-between py-12 absolute left-1/2 -translate-x-1/2 px-12 lg:px-24 z-50"
	>
		<div class="">
			<Button variant="ghost" href="/" class="p-0 text-lg text-background hover:bg-inherit">
				{WebsiteName}
			</Button>
		</div>
		<div class="">
			<ul class="px-1 hidden sm:flex place-items-center font-bold text-md text-background">
				{#if authState.user?.is_anonymous && !environment.value}
					<li class="md:mx-2">
						<Button
							href="/login/sign_in"
							class="w-full bg-background text-background rounded-3xl px-7 bg-foreground/60 border-2 border-foreground/50 font-bold hover:bg-background/80 hover:text-foreground/80"
							variant="outline"
						>
							Login
						</Button>
					</li>
				{/if}
				{#if !authState.user?.is_anonymous}
					<li class="md:mx-2">
						<Button
							href="/sign_out"
							class="w-full bg-background text-background rounded-3xl px-7 bg-foreground/60 border-2 border-foreground/50 font-bold hover:bg-background/80 hover:text-foreground/80"
						>
							Sign Out
						</Button>
					</li>
				{/if}
				<li class="md:mx-2">
					{#if environment.value}
						<Button
							href="/dashboard/{environment.value.slug}"
							class="w-full bg-background text-background rounded-3xl px-7 bg-foreground/60 border-2 border-foreground/50 font-bold hover:bg-background/80 hover:text-foreground/80"
						>
							Dashboard
						</Button>
					{/if}
				</li>
			</ul>

			<div class="sm:hidden">
				<DropDownMenu.Root>
					<DropDownMenu.Trigger asChild let:builder>
						<Button builders={[builder]}><Menu /></Button>
					</DropDownMenu.Trigger>
					<DropDownMenu.Content class="w-56 sm:hidden">
						<DropDownMenu.Item>
							<a href="/dashboard/{environment.value?.slug}" class="w-full">
								Dashboard
							</a>
						</DropDownMenu.Item>
					</DropDownMenu.Content>
				</DropDownMenu.Root>
			</div>
		</div>
	</div>

	{@render children()}
</div>
