<script lang="ts">
  import Button from "$lib/components/ui/button/button.svelte"
  import * as Dialog from "$lib/components/ui/dialog"
  import Typography from "$lib/components/ui/typography/typography.svelte"

  import type { Tables } from "$lib/supabase"
  import type { SuperValidated, Infer } from "sveltekit-superforms"
  import type { ProjectSchema } from "$lib/schemas"
  import ProjectForm from "./project-form.svelte"

  interface Props {
    data: {
      supabase: any
      session: any
      projects: Tables<"projects">[]
      projectForm: SuperValidated<Infer<ProjectSchema>>
    }
  }

  let { data }: Props = $props()

  let { supabase, session, projects: dataProjects } = data

  let projects: Tables<"projects">[] = $state(dataProjects || [])
  let selectedProject: string = $state("")


  let newProject: Tables<"projects"> | undefined = $state()

  $inspect(session)

</script>

<div class="flex flex-col gap-8">
  <Typography variant="display-lg">Projects</Typography>
  <Dialog.Root
    open={selectedProject != ""}
    onOpenChange={(open) => {
      if (!open) {
        selectedProject = ""
      }
    }}
  >
    <Dialog.Content class="">
      <Dialog.Header>
        <Dialog.Title>Project</Dialog.Title>
      </Dialog.Header>
      {#if selectedProject != ""}
        <ProjectForm
          projectForm={data.projectForm}
          project={projects.find((project) => project.id === selectedProject) || newProject}
        />
      {/if}
    </Dialog.Content>
  </Dialog.Root>
  <ul class="grid grid-cols-3 gap-4">
    <li class="col-span-3">
      <Button
        class="w-full"
        onclick={() => {
          newProject = {
            id: crypto.randomUUID(),
            profile_id: session.user.id,
            created_at: new Date().toISOString(),
            title: "new",
            prompt: "",
            running: false,
            subreddits: [],
          }
          selectedProject = newProject.id
        }}
      >
        Create New Project
      </Button>
    </li>
    {#each projects as project}
      <li class="bg-card border rounded-md">
        <Button
          class="w-full h-full flex flex-col p-6"
          variant="ghost"
          onclick={() => {
            selectedProject = project.id
          }}
        >
          <Typography variant="body-sm">Click to edit</Typography>
          <Typography variant="headline-md">{project.title}</Typography>
        </Button>
      </li>
    {/each}
  </ul>
</div>
