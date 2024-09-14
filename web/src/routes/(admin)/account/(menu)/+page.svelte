<script lang="ts">
  import * as Resizable from "$lib/components/ui/resizable"
  import DataTable from "$lib/components/ui/data-table/data-table.svelte"
  import * as ToggleGroup from "$lib/components/ui/toggle-group"
  import * as Select from "$lib/components/ui/select"
  import { LeadViewer } from "$lib/components/ui/lead-viewer"
  import type { Tables } from "$lib/supabase/database.types"
  import type { SupabaseClient } from "@supabase/supabase-js"
  import { Toggle } from "$lib/components/ui/toggle"
  import { BookCheck, Trash } from "lucide-svelte"
  import { Button } from "$lib/components/ui/button"

  interface Props {
    data: {
      supabase: SupabaseClient<any, "public", any>
      submissions: Tables<"submissions">[]
      projects: Tables<"projects">[]
    }
  }

  let { data }: Props = $props()

  const supabase = data.supabase;

  let selectedProject: {label: string, value: string} | undefined = $state({label: data.projects[0].title, value: data.projects[0].id})

  let submissions: Tables<'submissions'>[] = $state(data.submissions || [])

  supabase.channel('submissions').on('postgres_changes',
    {event: 'INSERT', schema: 'public', table: 'submission'},
    (payload) => {
        submissions.push(payload.new as Tables<'submissions'>)
    }
  )

  // Arbituarilly select the first submission
  let selectedSubmission: Tables<'submissions'> | null = $state(submissions[0] ?? null)

  let relevantSubmissions: Tables<'submissions'>[] = $derived(submissions.filter(
    (submission: Tables<'submissions'>) => submission.is_relevant === false))

  let includeRead: boolean = $state(false)
  let includeIrrelevant: boolean = $state(false)

  // List that is displayed
  let displaySubmissions = $derived.by(()=>{
    let _submissions: Tables<'submissions'>[] = []

    if (!selectedProject) return _submissions

    submissions.map((submission: Tables<'submissions'>) => {
      if (submission.project_id === selectedProject!.value) {
        if (!submission.is_relevant && includeIrrelevant) {
          _submissions.push(submission)
        }
        if (submission.done && includeRead) {
          _submissions.push(submission)
        }
        // If the submission is relevant and not done
        if (submission.is_relevant && !submission.done) {
          _submissions.push(submission)
        }
      }
    })

    return _submissions
    
  })

  $inspect(displaySubmissions)
  $inspect(data)
</script>

<Resizable.PaneGroup
  direction="horizontal"
  class="rounded-md border bg-background"
>
  <Resizable.Pane defaultSize={50}>
    <div class="flex flex-col p-2">
      <div class="flex flex-col place-items-center w-full justify-between">
        <Select.Root portal={null} bind:selected={selectedProject}>
          <div class="flex flex-col gap-y-0.5">
            <Select.Label class="text-left text-xl pl-0"
            >Select Project:</Select.Label
          >
          <Select.Trigger class="max-w-xl mb-8">
            <Select.Value placeholder="Select a project" />
          </Select.Trigger>
          <Select.Content>
            <Select.Group>
              {#each data.projects as project}
                <Select.Item
                  value={project.id}
                  label={project.title}
                  class="text-primary">{project.title}</Select.Item
                >
              {/each}
            </Select.Group>
          </Select.Content>
          </div>
          
        </Select.Root>
        <div class="flex flex-row gap-2">
          <Toggle bind:pressed={includeRead} class="gap-2 bg-card">
            <BookCheck /> Include Read 
          </Toggle>
          <Toggle bind:pressed={includeIrrelevant} class="gap-2 bg-card">
            <Trash /> Include Irrelevant
          </Toggle>
          </div>
          
      </div>
      <div class="overflow-y-scroll max-h-96 mt-4 flex flex-col gap-y-4 w-full">
        {#each displaySubmissions as submission}
          <Button class="text-wrap h-fit bg-card" variant="outline" on:click={() => selectedSubmission = submission}>
            {submission.title}
          </Button>
        {/each}
      </div>
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
