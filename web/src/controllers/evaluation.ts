import { fetchSubredditPosts } from "../redditClient/fetchSubredditPosts";
import { evaluatePostRelevance } from "../ai/agent/relevanceChecker";
import type { EvaluatedSubmission } from "../types/types";
import { summarizePost } from "../ai/agent/summarizer";

// Main function to process posts from Reddit
export async function processPosts(): Promise<EvaluatedSubmission[]> {
  try {
    // Fetch posts from the subreddit
    const posts = await fetchSubredditPosts();
    const evaluatedPosts: EvaluatedSubmission[] = [];

    // Process each post
    for (const post of posts) {
      // Summarize the post
      const summarizedPost = await summarizePost(post);
      // console.log("Summarized Post:", summarizedPost);
      // Evaluate the relevance of the summarized post
      const evaluatedPost = await evaluatePostRelevance(summarizedPost);
      // Add the evaluated post to our results
      evaluatedPosts.push(evaluatedPost);
      // Log the result
      console.log(evaluatedPost);
    }

    return evaluatedPosts;
  } catch (error) {
    console.error("Error processing posts:", error);
    throw error;
  }
}
