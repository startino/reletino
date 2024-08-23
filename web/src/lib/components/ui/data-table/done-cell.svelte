<script lang="ts">
  import { Check, CircleDashed } from "lucide-svelte";
  import { Button } from "$lib/components/ui/button";
  import { Input } from "$lib/components/ui/input";
  import { enhance } from "$app/forms";

  export let done: boolean;
</script>

{#key done}
  {#if done}
    <div class="flex items-center space-x-2">
      <Check size="24" class="text-green-500" />
    </div>
  {:else}
    <div class="flex items-center space-x-2">
      <CircleDashed size="24" class="text-orange-500" />
    </div>
  {/if}
{/key}
