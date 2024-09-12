<script lang="ts">
  import type { Tables } from "$lib/supabase/database.types"
  import * as Sheet from "$lib/components/ui/sheet/index.js";
  import { Button } from "$lib/components/ui/button/index.js";
  import { Input } from "$lib/components/ui/input/index.js";
  import { Label } from "$lib/components/ui/label/index.js";
  
  import { Textarea } from "$lib/components/ui/textarea/index.js";
  import { enhance } from "$app/forms"

  export let data: { projects: Tables<'projects'>[] };
    
  let { projects } = data;

</script>

{#each projects as project}
  <div class="flex items-center justify-center p-6">
    <Sheet.Root>
        <Sheet.Trigger asChild let:builder>
          <Button builders={[builder]} variant="outline">
            {#if project.running}
            <div class="h-3 w-3 rounded-full bg-primary animate-pulse mr-3"></div>
            {:else}
            <div class="h-3 w-3 rounded-full bg-orange-500 animate-pulse mr-3"></div>
            {/if}
            {project.title}</Button>
        </Sheet.Trigger>
        <Sheet.Content side="right">
          <Sheet.Header>
            <Sheet.Title>{project.title}</Sheet.Title>
            <Sheet.Description>
              Make changes to your profile here. Click save when you're done.
            </Sheet.Description>
          </Sheet.Header>
          <form id="project_{project.id}" class="grid gap-4 py-4" >
            <div class="flex flex-col items-start gap-4">
              <Label for="title" class="">Title</Label>
              <Input id="title" value={project.title} class="w-full" />
            </div>
            <div class="flex flex-col items-start gap-4">
              <Label for="description" class="">Subreddits</Label>
              <Input id="description" value={project.subreddits} placeholder="SaaS+futino+startup" class="w-full" />
            </div>
            <div class="flex flex-col items-start gap-4">
              <Label for="prompt" class="">Prompt</Label>
              <Textarea id="prompt" value={project.prompt} placeholder="Type your prompt here." />
            </div>
        </form>
          <Sheet.Footer>
            <Sheet.Close asChild let:builder>
              <Button builders={[builder]} form="project_{project.id}">Save changes</Button>
            </Sheet.Close>
          </Sheet.Footer>
        </Sheet.Content>
      </Sheet.Root>
  </div>
{/each}