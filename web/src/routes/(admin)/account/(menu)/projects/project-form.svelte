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
    import { toast } from "svelte-sonner";

    interface Props {
        projectForm: SuperValidated<Infer<ProjectSchema>>
        project: Tables<"projects">
    }

    let { projectForm, project = $bindable() }: Props = $props()

    const form = superForm(projectForm, {
        onSubmit: async () => {
        },
        validators: zodClient(projectSchema),
        resetForm: false,
        onResult: (result) => {
            console.log("Form result: ", result)
        },
        onUpdated({ form }) {
          if (form.message) {
            if (form.message.type == "error") {
              toast.error(form.message.text);
            } else if (form.message.type == "success") {
            toast.success(form.message.text);
          }
       }
    },
    })
    
    const { form: formData, errors, enhance, message } = form

    $effect(() => {
        $formData = project
    })

    let newSubreddit: string = $state("")

    const tryAddSubreddit = () => {
        if (newSubreddit != "") {
            $formData.subreddits = [...$formData.subreddits, newSubreddit]
        }
        newSubreddit = "";
    }

</script>

<form method="POST" action="?/updateProject" use:enhance>

  <input type="hidden" name="id" bind:value={$formData.id} />
  <input type="hidden" name="profile_id" bind:value={$formData.profile_id} />
    
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
        class="w-fit border-2 border-primary"
        placeholder="Type a subreddit here..."
        bind:value={newSubreddit}
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
  <Form.Field {form} name="prompt">
    <Form.Control let:attrs>
      <Form.Label>Prompt</Form.Label>
      <Form.Description>This is the project's title.</Form.Description>
      <Textarea {...attrs} bind:value={$formData.prompt} />
    </Form.Control>
    <Form.FieldErrors />
  </Form.Field>
  <Form.Button>Save</Form.Button>
</form>
