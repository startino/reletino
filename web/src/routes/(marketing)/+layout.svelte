<script lang="ts">
	import { Menu } from 'lucide-svelte';
	import { Button } from '$lib/components/ui/button';
	import * as DropDownMenu from '$lib/components/ui/dropdown-menu';
	import { getEnvironmentState, getAuthState } from '$lib/states';

	import { WebsiteName } from '$lib/config';

	let { children } = $props();
	const environment = getEnvironmentState();
	const authState = getAuthState();
</script>

<div class="relative h-dvh">
	<div class="relative z-50 flex w-full place-content-between px-12 py-12 lg:px-24">
		<div class="">
			<Button variant="ghost" href="/" class="text-background p-0 text-lg hover:bg-inherit">
				{WebsiteName}
			</Button>
		</div>
		<div class="">
			<ul class="text-md text-background hidden place-items-center px-1 font-bold sm:flex">
				{#if authState.user?.is_anonymous && !environment.value}
					<li class="md:mx-2">
						<Button
							href="/login/sign_in"
							class="bg-background text-background bg-foreground/60 border-foreground/50 hover:bg-background/80 hover:text-foreground/80 w-full rounded-3xl border-2 px-7 font-bold"
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
							class="bg-background text-background bg-foreground/60 border-foreground/50 hover:bg-background/80 hover:text-foreground/80 w-full rounded-3xl border-2 px-7 font-bold"
						>
							Sign Out
						</Button>
					</li>
				{/if}
				<li class="md:mx-2">
					{#if environment.value}
						<Button
							href="/dashboard/{environment.value.slug}"
							class="bg-background text-background bg-foreground/60 border-foreground/50 hover:bg-background/80 hover:text-foreground/80 w-full rounded-3xl border-2 px-7 font-bold"
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
