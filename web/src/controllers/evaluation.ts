import { fetchSubredditPosts } from "../redditClient/fetchSubredditPosts";
import { evaluatePostRelevance } from "../ai/agent/relevanceChecker";
import type { EvaluatedSubmission, Post } from "../types/types";
import { summarizePosts } from "../ai/agent/summarizer";

// Main function to process posts from Reddit
export async function processPosts(): Promise<EvaluatedSubmission[]> {
  try {
    // Fetch posts from the subreddit
    const posts: Post[] = await fetchSubredditPosts();
    console.log(`Fetched ${posts.length} posts from subreddit`);

    // Summarize all posts
    const summarizedPosts = await summarizePosts(posts);
    console.log(`Summarized ${summarizedPosts.length} posts`);

    const evaluatedPosts: EvaluatedSubmission[] = [];

    // Process each summarized post
    for (const summarizedPost of summarizedPosts) {
      // Evaluate the relevance of the summarized post
      const evaluatedPost = await evaluatePostRelevance(summarizedPost);

      // Add the evaluated post to our results
      evaluatedPosts.push(evaluatedPost);

      // Log the result
      console.log(`Evaluated post: ${summarizedPost.title}`);
      console.log(evaluatedPost);
    }

    return evaluatedPosts;
  } catch (error) {
    console.error("Error processing posts:", error);
    throw error;
  }
}
