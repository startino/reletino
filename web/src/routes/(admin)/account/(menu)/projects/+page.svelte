<script lang="ts">
  import Button from '$lib/components/ui/button/button.svelte'
  import * as Dialog from '$lib/components/ui/dialog';
  import Typography from '$lib/components/ui/typography/typography.svelte';

  import type { Tables } from '$lib/supabase';

  let { data } = $props();

  let {supabase, session, projects: dataProjects} = data;

  let projects: Tables<'projects'>[] = $state(dataProjects || []);
  let selectedProject: string = $state(projects![0].id || "");


</script>

<div class="flex flex-col gap-8">
  <Typography variant="display-lg">Projects</Typography>
  <Dialog.Root open={selectedProject != ""}>

  </Dialog.Root>
  <ul class="grid grid-cols-3 gap-4">
    <li class="col-span-3">
      <Button class="w-full" onclick={()=>{
        const newProject = {
          id: crypto.randomUUID(),
          created_at: new Date().toISOString(),
          title: "Untitled Project",
          profile_id: session!.user.id,
          prompt: "Empty Prompt",
          running: false,
          subreddits: ["saas", "startups"],
        };
        projects.push(newProject);
        selectedProject = newProject.id;
      }}
      >
        Create New Project
      </Button>
    </li>
      {#each projects as project}
        <li class="bg-card border rounded-md">
         
            <Button class="w-full h-full flex flex-col p-6" variant="ghost" onclick={()=>{
              selectedProject = project.id;
            }}
            >
            <Typography variant="body-sm">Click to edit</Typography>
            <Typography variant="headline-md">{project.title}</Typography>
            </Button>
        </li>
      {/each}
  </ul>
</div>


