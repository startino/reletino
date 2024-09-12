<script lang="ts">
  import * as Resizable from "$lib/components/ui/resizable";
  import DataTable from "$lib/components/ui/data-table/data-table.svelte";
  import * as Select from "$lib/components/ui/select";
  import { LeadViewer } from "$lib/components/ui/lead-viewer";
  import type { Tables } from "$lib/supabase/database.types"

  export let data: { relevantSubmissions: Tables<'submissions'>[], projects: Tables<'projects'>[] };

  let { relevantSubmissions, projects } = data;

  let selectedProject = {"value": projects[0].id, "label": projects[0].title};

  // Arbituarilly select the first submission
  let activeSubmission = relevantSubmissions[0];

  // Filter by project
  $: relevantSubmissions = relevantSubmissions.filter((row) => row.project_id === selectedProject.value);

  async function markAsDone(id: string) {
    relevantSubmissions = relevantSubmissions.map((row) => {
      if (row.id === id) {
        row.done = true;
      }
      return row;
    });

    const res = await fetch(`?/markAsDone`, {
      method: "POST",
      body: JSON.stringify({ id }),
    });
    const { success } = await res.json();
  }
</script>



<Resizable.PaneGroup direction="horizontal" class="rounded-lg border bg-background">
  <Resizable.Pane defaultSize={50}>
    <div class="flex flex-col p-6">
      <Select.Root portal={null}

      bind:selected={selectedProject}
>
        <Select.Label class="text-left text-xl pl-0">Selected Project</Select.Label>
        <Select.Trigger class="max-w-xl mb-8">
          <Select.Value placeholder="Select a project"  />
        </Select.Trigger>
        <Select.Content>
          <Select.Group>
           
            {#each projects as project}
              <Select.Item value={project.id} label={project.title} class="text-primary"
                >{project.title}</Select.Item
              >
            {/each}
          </Select.Group>
        </Select.Content>
        <Select.Input name="favoriteFruit" />
      </Select.Root>
      {#key relevantSubmissions}
        <DataTable bind:activesubmission={activeSubmission} data={relevantSubmissions} {markAsDone} />
      {/key}
    </div>
  </Resizable.Pane>
  <Resizable.Handle withHandle />
  <Resizable.Pane defaultSize={50}>
    {#if activeSubmission}
      <LeadViewer bind:submission={activeSubmission} />
    {:else}
      <div class="flex items-center justify-center p-6">
        <p class="text-muted-foreground">No submission selected</p>
      </div>
    {/if}
  </Resizable.Pane>
</Resizable.PaneGroup>
