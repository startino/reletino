<script lang="ts">
  import { format, formatDistanceToNowStrict } from "date-fns"
  import { Button, buttonVariants } from "$lib/components/ui/button"
  import { Separator } from "$lib/components/ui/separator"
  import { Textarea } from "$lib/components/ui/textarea"
  import * as Dialog from "$lib/components/ui/dialog"

  import type { Tables } from "$lib/supabase/database.types"

  import { toast } from "svelte-sonner"

  import { enhance } from "$app/forms"

  export let submission: Tables<"submissions">

  let url: string
  $: url = submission.url ?? ""
  let subreddit: string
  $: subreddit = extractSubreddit(url)

  function extractSubreddit(url: string): string {
    // Parse the URL
    const parsedUrl = new URL(url)

    // Extract the pathname
    const pathname = parsedUrl.pathname

    // Extract the subreddit name
    const parts = pathname.split("/")
    const subreddit = "r/" + parts[2] // Assuming the subreddit name is always the second component

    return subreddit
  }

  let reasonTextValue = "Post is irrelevant because"
  let commentTextValue = ""

  // Function to copy to clipboard so I can easily copy this to my sales
  // management Google Sheet :P
  async function copyToClipboard(submission: Tables<"submissions">) {
    try {
      const currentDate = new Date()
      const formattedDate = `${currentDate.getDate()}/${currentDate.getMonth() + 1}`
      const cells = [submission.author, submission.url, "", formattedDate]
      // "	" is the special key that Google sheets uses to separate cells.
      // Select the text to actually see the character since my theme can't see
      // it by default lol
      await navigator.clipboard.writeText(cells.join("	"))
      toast.success("submission Copied", {
        description: "",
      })
    } catch (err) {
      console.error("Failed to copy: ", err)
    }
  }
</script>

<div class="flex h-full flex-col">
  {#if submission}
    <div class="flex h-full flex-1 flex-col overflow-hidden text-left">
      <div class="flex items-start p-4">
        <h1 class="bold text-2xl">{submission.title}</h1>
        <div class="ml-auto text-sm text-muted-foreground">
          Posted {formatDistanceToNowStrict(submission.submission_created_utc, {
            addSuffix: true,
          })}
          <br />
          {format(submission.submission_created_utc, "dd/MM")}
        </div>
      </div>
      <div class="flex flex-col gap-3 p-4">
        <h3><b class="pr-2">Username:</b> {submission.author}</h3>
        <h3><b class="pr-2">Subreddit:</b>{subreddit}</h3>
        <a href={url} target="_blank" class="text-accent underline"
          >Got to post</a
        >
        <div class="flex flex-row items-center gap-4">
          <Button
            class="w-fit"
            on:click={() => {
              copyToClipboard(submission)
            }}>Copy submission</Button
          >
        </div>
      </div>
      <Separator />
      <div
        class="flex-1 overflow-y-auto whitespace-pre-wrap p-4 text-left text-sm"
      >
        <p class="text-md tracking-widest">{submission.selftext}</p>
      </div>
      <Separator class="mt-auto" />
      <div class="p-4">
        <form>
          <div class="grid gap-4">
            <Textarea
              class="h-64 p-4"
              placeholder={`Reply ${submission.id}...`}
            />
          </div>
        </form>
      </div>
    </div>
  {:else}
    <div class="p-8 text-center text-muted-foreground">
      No submission selected
    </div>
  {/if}
</div>
