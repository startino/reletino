<script lang="ts">
  import * as Resizable from "$lib/components/ui/resizable"
  import DataTable from "$lib/components/ui/data-table/data-table.svelte"
  import * as ToggleGroup from "$lib/components/ui/toggle-group"
  import * as Select from "$lib/components/ui/select"
  import { LeadViewer } from "$lib/components/ui/lead-viewer"
  import type { Tables } from "$lib/supabase/database.types"

  interface Props {
    data: {
      submissions: Tables<"submissions">[]
      projects: Tables<"projects">[]
    }

  }

  let { data } = $props()

  let selectedProject = $state({ value: "", label: "No projects" })

  // Arbituarilly select the first submission
  let selectedSubmission: Tables<'submissions'> | null = $state(null)

  // Filter by project
  $effect(()=>{
    data.relevantSubmissions = data.relevantSubmissions.filter(
      (submission: Tables<'projects'>) => submission.project_id === selectedProject.value)
  })

</script>

<Resizable.PaneGroup
  direction="horizontal"
  class="rounded-lg border bg-background"
>
  <Resizable.Pane defaultSize={50}>
    <div class="flex flex-col p-6">
      <div class="flex flex-row">
        <Select.Root portal={null} bind:selected={selectedProject}>
          <Select.Label class="text-left text-xl pl-0"
            >Selected Project</Select.Label
          >
          <Select.Trigger class="max-w-xl mb-8">
            <Select.Value placeholder="Select a project" />
          </Select.Trigger>
          <Select.Content>
            <Select.Group>
              {#each projects as project}
                <Select.Item
                  value={project.id}
                  label={project.title}
                  class="text-primary">{project.title}</Select.Item
                >
              {/each}
            </Select.Group>
          </Select.Content>
          <Select.Input name="favoriteFruit" />
        </Select.Root>
        <ToggleGroup.Root type="multiple">
          <ToggleGroup.Item value="bold" aria-label="Toggle bold">
            Include Read
          </ToggleGroup.Item>
          <ToggleGroup.Item value="italic" aria-label="Toggle italic">
            Include Irrelevant
          </ToggleGroup.Item>
        </ToggleGroup.Root>
      </div>

        {#each relevantSubmissions as submission}
          <div class="w-full p-4 border">
            {submission.title}
          </div>
        {/each}
    </div>
  </Resizable.Pane>
  <Resizable.Handle withHandle />
  <Resizable.Pane defaultSize={50}>
    {#if selectedSubmission}
      <LeadViewer bind:submission={selectedSubmission} />
    {:else}
      <div class="flex items-center justify-center p-6">
        <p class="text-muted-foreground">No submission selected</p>
      </div>
    {/if}
  </Resizable.Pane>
</Resizable.PaneGroup>
