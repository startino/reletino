import { fetchSubredditPosts } from "../redditClient/fetchSubredditPosts";
import { evaluatePostRelevance } from "../ai/agent/relevanceChecker";
import type { EvaluatedSubmission, Post } from "../types/types";

export async function processPosts(): Promise<EvaluatedSubmission[]> {
  try {
    const posts: Post[] = await fetchSubredditPosts();
    console.log(`Fetched ${posts.length} posts from subreddit`);

    const evaluatedPosts: EvaluatedSubmission[] = [];

    for (const post of posts) {
      const evaluatedPost = await evaluatePostRelevance(post);
      evaluatedPosts.push(evaluatedPost);

      console.log(`Evaluated post: ${post.title}`);
      console.log(evaluatedPost);
    }

    return evaluatedPosts;
  } catch (error) {
    console.error("Error processing posts:", error);
    throw error;
  }
}
