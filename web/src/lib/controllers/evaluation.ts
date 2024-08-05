import { fetchSubredditPosts } from "../redditClient/fetchSubredditPosts";
import { evaluatePostRelevance } from "../ai/agent/relevanceChecker";
import type { EvaluatedSubmission, Post } from "../types/types";
import type { TablesInsert } from "$lib/types/supabase";
import { saveEvaluatedPosts } from "$lib/db";

export async function processPosts(): Promise<void> {
  try {
    const posts: Post[] = await fetchSubredditPosts();
    // console.log("Fetched posts count:", posts.length);
    const evaluatedPosts: EvaluatedSubmission[] = [];
    for (const post of posts) {
      const evaluatedPost = await evaluatePostRelevance(post);
      evaluatedPosts.push(evaluatedPost);
    }

    // console.log("Evaluated posts count:", evaluatedPosts.length);

    const postsToInsert: TablesInsert<"evaluated_submissions">[] =
      evaluatedPosts.map((post) => ({
        body: post.post.selftext,
        reddit_id: post.post.reddit_id,
        is_relevant: post.is_relevant,
        qualifying_question: null,
        reason: post.reason,
        title: post.post.title,
        url: post.post.url,
      }));

    // console.log("Posts prepared for insertion:", postsToInsert.length);
    // console.log("Sample post to insert:", postsToInsert[0]);

    await saveEvaluatedPosts(postsToInsert);

    console.log("All posts have been processed and saved successfully");
  } catch (error) {
    console.error("Error processing and saving posts:", error);
    throw error;
  }
}
