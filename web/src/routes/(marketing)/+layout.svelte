<script lang="ts">
  import { Menu } from "lucide-svelte"
  import { Button, buttonVariants } from "$lib/components/ui/button"
  import * as DropDownMenu from "$lib/components/ui/dropdown-menu"
  import { getEnvironmentState, getAuthState } from "$lib/states"

  import { WebsiteName } from "$lib/config"

  let { children } = $props()
  const environment = getEnvironmentState()
  const authState = getAuthState()
</script>

<div class="h-dvh">
  <div class="flex py-4 container mx-auto sticky">
    <div class="flex-1">
      <Button variant="ghost" href="/" class="text-lg">
        {WebsiteName}
      </Button>
    </div>
    <div class="flex-none">
      <ul class="px-1 hidden sm:flex font-bold text-lg">
        {#if authState.user?.is_anonymous && !environment.value}
          <li class="md:mx-2">
            <a
              href="/login/sign_in"
              class={buttonVariants({ variant: "outline" })}>Sign In</a
            >
          </li>
        {/if}
        {#if !authState.user?.is_anonymous}
          <li class="md:mx-2">
            <a href="/sign_out" class={buttonVariants({ variant: "ghost" })}
              >Sign Out</a
            >
          </li>
        {/if}
        <li class="md:mx-2">
          {#if !environment.value}
            <a
              href="/onboarding"
              class={buttonVariants({ variant: "default" })}
            >
              Get Started
            </a>
          {:else}
            <a
              href="/dashboard/{environment.value.slug}"
              class={buttonVariants({ variant: "default" })}
            >
              Dashboard
            </a>
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
              <a href="/dashboard/{environment.value?.slug}" class="w-full"
                >Dashboard</a
              >
            </DropDownMenu.Item>
          </DropDownMenu.Content>
        </DropDownMenu.Root>
      </div>
    </div>
  </div>

  {@render children()}
</div>
