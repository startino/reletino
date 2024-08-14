import { fetchSubredditPosts } from "$lib/server/redditClient/fetchSubredditPosts";
import { evaluatePostRelevance } from "../ai/agent/relevanceChecker";
import type { EvaluatedSubmission, Post } from "../../types/types";
import type { TablesInsert } from "$lib/supabase/database.types";
import { saveEvaluatedSubmissions, saveLeads } from "../db";

export async function fetchPostAndEvaluate(): Promise<void> {
  const posts: Post[] = await fetchSubredditPosts();
  console.log("Posts fetched successfully.......");

  const evaluatedPosts: EvaluatedSubmission[] = [];

  for (const post of posts) {
    const evaluatedPost = await evaluatePostRelevance(post);
    evaluatedPosts.push(evaluatedPost);
    console.log("Evaluated post:", evaluatedPost.post.title);
  }

  const submissionsToSave: TablesInsert<"evaluated_submissions">[] =
    evaluatedPosts.map((evaluatedPost) => ({
      body: evaluatedPost.post.selftext,
      reddit_id: evaluatedPost.post.reddit_id,
      is_relevant: evaluatedPost.is_relevant,
      qualifying_question: evaluatedPost.qualifying_question,
      reason: evaluatedPost.reason,
      title: evaluatedPost.post.title,
      url: evaluatedPost.post.url,
    }));

  const savedSubmissionData = await saveEvaluatedSubmissions(submissionsToSave);

  if (savedSubmissionData.length > 0) {
    console.log(`${savedSubmissionData.length} new submissions saved`);

    const leads: TablesInsert<"leads">[] = savedSubmissionData
      .map((savedSubmission, index) => {
        const evaluatedPost = evaluatedPosts[index];
        if (!savedSubmission.is_relevant) {
          return null;
        }
        return {
          submission_id: savedSubmission.id,
          prospect_username: evaluatedPost.post.author,
          source: "their_post",
          last_event: "discovered",
          status: "under_review",
          data: {
            title: evaluatedPost.post.title,
            body: evaluatedPost.post.selftext,
            url: evaluatedPost.post.url,
          },
          reddit_id: evaluatedPost.post.reddit_id,
          comment: null,
        };
      })
      .filter((lead) => lead !== null);

    await saveLeads(leads);
    console.log(`${leads.length} new leads saved`);
  } else {
    console.log("No new submissions to save. Skipping to update lead.");
  }
}
