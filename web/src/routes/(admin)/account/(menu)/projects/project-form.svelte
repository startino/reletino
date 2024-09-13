<script lang="ts">
  import { Button } from "$lib/components/ui/button"
  import * as Form from "$lib/components/ui/form"
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

  interface Props {
    projectForm: SuperValidated<Infer<ProjectSchema>>
    project: Tables<"projects">
  }

  let { projectForm, project = $bindable() }: Props = $props()

  const form = superForm(projectForm, {
    validators: zodClient(projectSchema),
  })

  const { form: formData, errors, enhance } = form

  $effect(() => {
    $formData = project
  })

  const defaultNewSubredditText: string = "Type a subreddit here..."
  let newSubreddit: string = $state(defaultNewSubredditText)

  const tryAddSubreddit = () => {
    if (newSubreddit != "" && newSubreddit != defaultNewSubredditText) {
            {
              $formData.subreddits = [...$formData.subreddits, newSubreddit]
            }
            newSubreddit = defaultNewSubredditText
          } else {
            newSubreddit = defaultNewSubredditText
          }
        }
  
</script>

<form method="POST" action="?/updateProject" use:enhance>
  <Form.Field {form} name="title">
    <Form.Control let:attrs>
      <Form.Label>Title</Form.Label>
      <Form.Description>This is the project's title.</Form.Description>
      <Input {...attrs} bind:value={$formData.title} />
    </Form.Control>

    <Form.FieldErrors />
  </Form.Field>

  <Form.Field {form} name="subreddits">
    <Form.Control let:attrs>
      <Form.Label>Subreddits</Form.Label>
      <Form.Description>Type in the box below.</Form.Description>
      <Input
        class="w-fit border-2 border-primary "
        bind:value={newSubreddit}
        on:focusin={() => {
          if (newSubreddit == defaultNewSubredditText) {
            newSubreddit = ""
          }
        }}
        on:keydown={(e) => {
          if (e.key == "Enter") {
            tryAddSubreddit()
            newSubreddit = ""
          }
        }}
        on:focusout={tryAddSubreddit}
      />
      <div class="grid grid-cols-4 gap-3 mt-4">
        {#each $formData.subreddits as _, i}
            <Button variant="outline" class="w-full h-fit rounded-md flex flex-row justify-between hover:bg-destructive/20 px-2 py-1" 
            on:click={() => {
                $formData.subreddits = $formData.subreddits.filter(
                (subreddit) => subreddit != $formData.subreddits[i]
                )
            }} >
            <Typography variant="body-md" class="">
                {$formData.subreddits[i]}
            </Typography>
            <X class="text-destructive" />
        
        </Button>
        {/each}
      </div>
    </Form.Control>
    
    <Form.FieldErrors />
  </Form.Field>
  <Form.Field {form} name="title">
    <Form.Control let:attrs>
      <Form.Label>Prompt</Form.Label>
      <Form.Description>This is the project's title.</Form.Description>
      <Textarea {...attrs} bind:value={$formData.prompt} />
    </Form.Control>
    <Form.FieldErrors />
  </Form.Field>
</form>
