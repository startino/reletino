<script lang="ts">
  import * as Resizable from "$lib/components/ui/resizable";
  import DataTable from "$lib/components/ui/data-table/data-table.svelte";
  import * as Select from "$lib/components/ui/select";
  
  import { LeadViewer } from "$lib/components/ui/lead-viewer";
  import type { Tables } from "$lib/supabase/database.types"

  export let data: { relevantSubmissions: Tables<'submissions'>[] };

  let { relevantSubmissions } = data;

  let activeSubmission = relevantSubmissions[0];

  let projects = [
    { value: "uuid-here-special", label: "Project One" },
    { value: "a-unique-uuid", label: "Project Two" },
    { value: "very-special-uuid", label: "Project Three" },
  ];

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

<Resizable.PaneGroup direction="horizontal" class="rounded-lg border">
  <Resizable.Pane defaultSize={50}>
    <div class="flex items-center justify-center p-6">
      <Select.Root portal={null}>
        <Select.Trigger class="w-[180px]">
          <Select.Value placeholder="Select a fruit" />
        </Select.Trigger>
        <Select.Content>
          <Select.Group>
            <Select.Label>Fruits</Select.Label>
            {#each projects as project}
              <Select.Item value={project.value} label={project.label}
                >{project.label}</Select.Item
              >
            {/each}
          </Select.Group>
        </Select.Content>
        <Select.Input name="favoriteFruit" />
      </Select.Root>
      {#key relevantSubmissions}
        <DataTable bind:activeLead={activeSubmission} data={relevantSubmissions} {markAsDone} />
      {/key}
    </div>
  </Resizable.Pane>
  <Resizable.Handle withHandle />
  <Resizable.Pane defaultSize={50}>
    <LeadViewer bind:lead={activeSubmission} />
  </Resizable.Pane>
</Resizable.PaneGroup>
