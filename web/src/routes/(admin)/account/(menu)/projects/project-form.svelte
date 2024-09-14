<script lang="ts">
  import { Button } from "$lib/components/ui/button"
  import * as Dialog from "$lib/components/ui/dialog"
  import * as Form from "$lib/components/ui/form"
  import * as Select from "$lib/components/ui/select"
  import { Input } from "$lib/components/ui/input"
  import { Textarea } from "$lib/components/ui/textarea"
  import { projectSchema, type ProjectSchema } from "$lib/schemas"
  import type { Tables } from "$lib/supabase"
  import {
    superForm,
    type SuperForm,
    type SuperValidated,
    type Infer,
  } from "sveltekit-superforms"
  import { zodClient } from "sveltekit-superforms/adapters"
  import { X } from "lucide-svelte"
  import { Typography } from "$lib/components/ui/typography"
  import { toast } from "svelte-sonner"
  import type { SupabaseClient, Session } from "@supabase/supabase-js"
  import { Switch } from "$lib/components/ui/switch"

  interface Props {
    session: Session
    supabase: SupabaseClient<any, "public", any>
    projectForm: SuperValidated<Infer<ProjectSchema>>
    selectedProjectId: string
    newProject: Tables<"projects"> | null
    projects: Tables<"projects">[]
  }

  let {
    session,
    supabase,
    projectForm,
    selectedProjectId = $bindable(),
    projects = $bindable(),
    newProject = $bindable(),
  }: Props = $props()

  let selectedProject: Tables<"projects"> =
    newProject ?? projects.find((project) => project.id == selectedProjectId)!

  const form = superForm(projectForm, {
    onSubmit: async () => {
      console.log("subreddits", $formData.subreddits)
      newProject = null
    },
    validators: zodClient(projectSchema),
    resetForm: false,
    onResult: ({ result, formElement, cancel }) => {
      if (result.type == "success") {
        if (!projects.some(project => project.id === $formData.id)) {
          projects.push($formData as Tables<"projects">);
        }
      }
    },
    onUpdated({ form }) {
      if (form.message) {
        if (form.message.type == "error") {
          toast.error(form.message.text)
        } else if (form.message.type == "success") {
          toast.success(form.message.text)
        }
      }
    },
  })

  const { form: formData, errors, enhance, message } = form

  $effect(() => {
    $formData = selectedProject
    console.log("project id", selectedProjectId)
  })

  let subreddits: { label: string, value: string }[] = $derived($formData.subreddits.map((subreddit) => ({ label: subreddit, value: subreddit })));

  let newSubreddit: string = $state("")

  const addSubreddit = () => {
    if (newSubreddit != "") {
      $formData.subreddits = [...$formData.subreddits, newSubreddit]
    }
    newSubreddit = ""
  }

  const deleteProject = async () => {
    const { data, error } = await supabase
      .from("projects")
      .delete()
      .eq("id", selectedProjectId)
      .select()
    if (error) {
      toast.error("An error occurred. Try again.")
    } else if (!data) {
      console.log(data)
      toast.error("Could not delete project. Project not found.")
    } else {
      projects = projects.filter((project) => project.id != selectedProjectId)
      selectedProjectId = ""
      toast.success("Project successfully deleted.")
    }
  }
</script>

<form method="POST" action="?/updateProject" class="flex flex-col gap-y-4" use:enhance >
  <input type="hidden" name="id" bind:value={$formData.id} />
  <input type="hidden" name="profile_id" bind:value={$formData.profile_id} />
  <!-- this button has to be here for disabling submit on enter when focusing on input fields-->
  <!-- https://github.com/sveltejs/kit/discussions/8657 -->
  <button type="submit" disabled style="display: none" />

  <Form.Field {form} name="title">
    <Form.Control let:attrs>
      <Form.Label>Title</Form.Label>
      <Form.Description>This is the project's title.</Form.Description>
      <Input {...attrs} bind:value={$formData.title} />
    </Form.Control>

    <Form.FieldErrors />
  </Form.Field>

  <Form.Field {form} name="subreddits" class="flex flex-col rounded-lg border p-4 pb-0">
    <Form.Control let:attrs>
      <div class="flex flex-row items-center justify-between">
      <div class="space-y-0.5">
        <Form.Label>Subreddits</Form.Label>
        <Form.Description>Subreddits will be shown below.</Form.Description>
      </div>
      <Input
        class="w-fit border-2 border-primary"
        placeholder="Type a subreddit here..."
        bind:value={newSubreddit}
        on:keydown={(e) => {
          if (e.key == "Enter") {
            addSubreddit()
            newSubreddit = ""
          }
        }}
        on:focusout={addSubreddit}
      />
      </div>
      <div class="grid grid-cols-4 gap-3 pt-4">
        {#if $formData.subreddits.length == 0}
          <Typography variant="body-md" class="col-span-4 text-center">
            No subreddits yet.
          </Typography>
        {:else}
        <Select.Root
        {...attrs}
				multiple
				selected={subreddits}
			  >
        {#each $formData.subreddits as subreddits}
          <input name={attrs.name} hidden value={subreddits} />
        {/each}
			  </Select.Root>
          {#each $formData.subreddits as _, i}
            <Button
              variant="outline"
              class="w-full h-fit rounded-md flex flex-row justify-between hover:bg-destructive/20 px-2 py-1"
              on:click={() => {
                $formData.subreddits = $formData.subreddits.filter(
                  (subreddit) => subreddit != $formData.subreddits[i],
                )
              }}
            >
              <Typography variant="body-md" class="">
                {$formData.subreddits[i]}
              </Typography>
              <X class="text-destructive" />
            </Button>
          {/each}
        {/if}
      </div>
    </Form.Control>

    <Form.FieldErrors />
  </Form.Field>
  <Form.Field {form} name="prompt">
    <Form.Control let:attrs>
      <Form.Label>Prompt</Form.Label>
      <Form.Description>This is the project's title.</Form.Description>
      <Textarea {...attrs} bind:value={$formData.prompt} />
    </Form.Control>
    <Form.FieldErrors />
  </Form.Field>
    <Form.Field
      {form}
      name="running"
      class="flex flex-row items-center justify-between rounded-lg border p-4"
    >
      <Form.Control let:attrs>
        <div class="space-y-0.5">
          <Form.Label>Running</Form.Label>
          <Form.Description>Turn on to start listening for Reddit posts.</Form.Description>
        </div>
        <Switch includeInput {...attrs} bind:checked={$formData.running} />
      </Form.Control>
    </Form.Field>
  <Form.Button class="mt-2">Save</Form.Button>
  {#if !newProject}
    <Dialog.Root>
      <Dialog.Trigger>
        <Button variant="destructive" class="w-full mt-6">Delete</Button>
      </Dialog.Trigger>
      <Dialog.Content class="place-items-center">
        <Dialog.Header>
          <Dialog.Title class="text-center"
            >YOU ARE ABOUT TO DELETE THIS PROJECT.</Dialog.Title
          >
        </Dialog.Header>

        <Typography variant="body-md">
          Are you sure you want to delete this project?
        </Typography>

        <Dialog.Footer>
          <Button
            class="w-full"
            variant="destructive"
            on:click={() => deleteProject()}
          >
            If I click this, I am sure.
          </Button>
        </Dialog.Footer>
      </Dialog.Content>
    </Dialog.Root>
  {/if}
</form>
