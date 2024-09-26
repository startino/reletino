<script lang="ts">
  import * as Resizable from "$lib/components/ui/resizable"
  import DataTable from "$lib/components/ui/data-table/data-table.svelte"
  import * as ToggleGroup from "$lib/components/ui/toggle-group"
  import * as Select from "$lib/components/ui/select"
  import SubmissionViewer from "./submission-viewer.svelte"
  import type { Tables } from "$lib/supabase/database.types"
  import type { SupabaseClient } from "@supabase/supabase-js"
  import { Toggle } from "$lib/components/ui/toggle"
  import { BookCheck, Trash, LocateOff, CheckCheck } from "lucide-svelte"
  import { Button } from "$lib/components/ui/button"
  import { Typography } from "$lib/components/ui/typography"
  import { onMount } from "svelte"
  import { invalidate } from "$app/navigation"
  import { page } from "$app/stores"

  interface Props {
    data: {
      supabase: SupabaseClient<any, "public", any>
      submissions: Tables<"submissions">[]
      projects: Tables<"projects">[]
    }
  }

  let { data }: Props = $props()

  const { supabase } = data

  let selectedProject: { label: string; value: string } | undefined = $state(
    data.projects.length > 0
      ? { label: data.projects[0].title, value: data.projects[0].id }
      : undefined,
  )

  let submissions: Tables<"submissions">[] = $state(data.submissions || [])

  supabase
    .channel("submissions")
    .on(
      "postgres_changes",
      { event: "INSERT", schema: "public", table: "submission" },
      (payload) => {
        submissions.push(payload.new as Tables<"submissions">)
      },
    )

  // Arbituarilly select the first submission
  let selectedSubmission: Tables<"submissions"> | null = $state(
    submissions[0] ?? null,
  )

  let relevantSubmissions: Tables<"submissions">[] = $derived(
    submissions.filter(
      (submission: Tables<"submissions">) => submission.is_relevant === false,
    ),
  )

  let includeRead: boolean = $state(false)
  let includeIrrelevant: boolean = $state(false)

  // List that is displayed
  let displaySubmissions = $derived.by(() => {
    let _submissions: Tables<"submissions">[] = []

    if (!selectedProject) return _submissions

    submissions.map((submission: Tables<"submissions">) => {
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

  onMount(async () => {
    invalidate("data:init")
  })
</script>

{#if data.projects.length == 0}
  <div class="flex flex-col place-items-center gap-6">
    <Typography variant="headline-lg" class="text-center">
      No projects found
    </Typography>
    <Button
      class="w-fit"
      href="/dashboard/{$page.data.environment.slug}/projects"
      >Create a new project</Button
    >
  </div>
{:else}
  <div class="grid grid-cols-5 grid-rows-5 gap-6 h-full">
    <div class="flex flex-col p-2 col-span-2 row-span-5">
      <div class="flex flex-col place-items-start w-full justify-between mb-4">
        <Select.Root portal={null} bind:selected={selectedProject}>
          <div class="flex flex-col gap-y-0.5">
            <Select.Label class="text-left pl-0">
              <Typography variant="headline-md">Project:</Typography>
            </Select.Label>
            <Select.Trigger class="mb-4 bg-card border-none">
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
          <Toggle variant="outline" bind:pressed={includeRead} class="gap-2">
            <CheckCheck /> Include Read
          </Toggle>
          <Toggle
            variant="outline"
            bind:pressed={includeIrrelevant}
            class="gap-2"
          >
            <LocateOff /> Include Irrelevant
          </Toggle>
        </div>
      </div>

      <div class="h-fit mt-4 overflow-y-scroll flex flex-col gap-y-6 w-full">
        <Typography variant="headline-md" class="text-left"
          >Submissions ({displaySubmissions.length})</Typography
        >
        {#each displaySubmissions as submission}
          <Button
            class="text-wrap text-left h-fit mx-2 grid grid-cols-7 {selectedSubmission ==
            submission
              ? 'bg-accent'
              : ''}"
            variant="outline"
            on:click={() => (selectedSubmission = submission)}
          >
            <div class="col-span-6">
              {submission.title}
            </div>
            <div class="ml-auto col-span-1">
              {#if submission.done}
                <CheckCheck class="w-5" />
              {/if}
              {#if !submission.is_relevant}
                <LocateOff class="w-5 " />
              {/if}
            </div>
          </Button>
        {/each}
      </div>
    </div>

    <div class="col-span-3 row-span-5">
      {#if selectedSubmission}
        <SubmissionViewer {supabase} bind:submission={selectedSubmission} bind:projectName={selectedProject.label} />
      {:else}
        <div class="flex items-center justify-center p-6">
          <p class="text-muted-foreground">No submission selected</p>
        </div>
      {/if}
    </div>
  </div>
{/if}
