<script lang="ts">
  import { Button } from "$lib/components/ui/button"
  import { cn } from "$lib/utils"

  export let id: string
  export let done: boolean
</script>

<Button
  class={cn("bg-primary text-white")}
  on:click={() => {
    console.log("Button clicked, ", id)
  }}
  disabled={done}
>
  Done
</Button>
