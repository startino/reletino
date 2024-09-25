<script lang="ts">
  import { format, formatDistanceToNowStrict } from "date-fns"
  import { Button, buttonVariants } from "$lib/components/ui/button"
  import { Separator } from "$lib/components/ui/separator"
  import { Textarea } from "$lib/components/ui/textarea"
  import * as Dialog from "$lib/components/ui/dialog"
  import critino from "$lib/apis/critino"

  import type { Tables } from "$lib/supabase/database.types"

  import { toast } from "svelte-sonner"

  import { enhance } from "$app/forms"
  import { Typography } from "$lib/components/ui/typography"
  import type { SupabaseClient } from "@supabase/supabase-js"
  import { CheckCheck, ExternalLink } from "lucide-svelte"

  interface Props {
    supabase: SupabaseClient<any, "public", any>
    submission: Tables<"submissions">
  }

  let { supabase, submission = $bindable() }: Props = $props()

  let url = submission.url
  let subreddit = submission.subreddit

  // Function to copy to clipboard so I can easily copy this to my sales
  // management Google Sheet :P
  async function copyToClipboard(submission: Tables<"submissions">) {
    try {
      const currentDate = new Date()
      const formattedDate = `${currentDate.getDate()}/${currentDate.getMonth() + 1}`
      const cells = [submission.author, submission.url, "", formattedDate]
      // "	" is the special key that Google sheets uses to separate cells.
      // Select the text to actually see the character s`in`ce my theme can't see
      // it by default lol
      await navigator.clipboard.writeText(cells.join("	"))
      toast.success("submission Copied", {
        description: "",
      })
    } catch (err) {
      console.error("Failed to copy: ", err)
    }
  }

  async function markAsRead() {
      const { data, error } = await supabase.from("submissions").update({
        done: true,
      }).eq("id", submission.id).select("*")
      if (error || !data) {
        toast.error("Failed to mark as read");
      }
      submission.done = true
      toast.success("Marked as read")
    }
    
    const handleCritique = async (submission: Tables<'submissions'>) => {
      const context = "";
      const query = `<title>${submission.title}</title><selftext>${submission.selftext}</selftext>`;
      const response = `{"reasoning": ${submission.reasoning}, "is_relevant": ${submission.is_relevant}}`;
      const team_name = "startino";
      const workflow_name = submission.project_id;
      const project_name = "reletino";
      const agent_name = "main";

      const tags: string[] = [];

      // will be set by the user in the critique editor
      const optimal: string = '';

      const body = {
          id: submission.id,
          context,
          query,
          optimal,
          response,
          team_name,
          project_name,
          workflow_name,
          agent_name,
      };
      console.log('body:', JSON.stringify(body, null, 2));
      const res = await critino.POST('/critiques', { body });
      if (res.data) {
          window.location = res.data;
          return;
      }

      if (res.error) {
          console.dir(res);
          console.error(
              `Error:\nMessage: ${res.error.detail.message}\n${res.error.detail.traceback}`
          );
          toast.error(`Error sending message: ${res.error.detail.message}`);
          return;
      }
    }
  
</script>

<div class="flex h-full flex-col">
  {#if submission}
    <div class="flex h-full flex-col ">
      <Typography variant="headline-md" class="text-left p-4">
        Post
        </Typography>
      <div class="flex flex-row text-left justify-between p-4">
        <div>
        <Typography variant="title-md" class="text-left">
          Title: {submission.title}
          </Typography>
          <Typography variant="title-md" class="text-left">
          Posted: {formatDistanceToNowStrict(submission.submission_created_utc, {
            addSuffix: false,
          })} ago,

          on  {format(submission.submission_created_utc, "dd/MM")}
        </Typography>
        <Typography variant="title-md" class="text-left">Author: {submission.author}</Typography>
        <Typography variant="title-md" class="text-left">Subredit: {submission.subreddit}</Typography>
    </div>
    <Button href={url} target="_blank" variant="default" class="mt-2">
      Visit Post <ExternalLink class="ml-2 w-5" />
    </Button>
      
      
      </div>

      <Separator />
      <div
        class="flex-1 overflow-y-auto whitespace-pre-wrap p-4 text-left text-sm"
      >
        <Typography variant="body-md" class="text-left">{submission.selftext}</Typography>
      </div>
   
      
      <Separator  />
      <div class="flex flex-col p-4 self-end">
        <Typography variant="title-lg" class="text-left">
          {submission.is_relevant ? 'Relevant' : 'Irrelevant'}
        </Typography>
        <Typography variant="title-md" class="text-left">
          Reasoning
        </Typography>
        <Typography variant="body-md" class="text-left">
          {submission.reasoning}
        </Typography>
      </div>
  
    
      <Separator />
      <div class="grid grid-cols-2 gap-6 w-full p-4">
        <Button onclick={() => handleCritique(submission)} target="_blank">
          Create Critino Review <ExternalLink class="ml-2 w-5" />
         </Button>
        <Button onclick={()=>markAsRead()}>
          Mark as Read <CheckCheck class="ml-2 w-5" />
        </Button>
      </div>
    </div>
  {:else}
    <div class="p-8 text-center text-muted-foreground">
      No submission selected
    </div>
  {/if}
</div>
