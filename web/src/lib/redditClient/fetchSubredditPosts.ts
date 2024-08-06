import { supabase } from "$lib/supabase";
import { authenticate, userAgent } from "./authenticate";
import { type Post } from "../types/types";

// List of subreddit names to fetch posts from
const SUBREDDIT_NAMES =
  "SaaS+SaaSy+startups+YoungEntrepreneurs+NoCodeSaas+nocode+cofounder+Entrepreneur+futino";

// Function to fetch posts from relevant subreddits
export async function fetchSubredditPosts(
  limit = 15, // Number of posts to fetch per page
  maxPages = 1 // Maximum number of pages to fetch
): Promise<Post[]> {
  // Authenticate and get access token
  const accessToken = await authenticate();
  let posts: Post[] = [];
  let after = null; // Used for pagination to get the next set of posts

  // Loop through the number of pages specified by maxPages
  for (let page = 0; page < maxPages; page++) {
    let url = `https://oauth.reddit.com/r/${SUBREDDIT_NAMES}/new.json?limit=${limit}`;
    if (after) {
      url += `&after=${after}`;
    }

    try {
      const response = await fetch(url, {
        headers: {
          Authorization: `Bearer ${accessToken}`,
          "User-Agent": userAgent,
        },
      });

      if (!response.ok) {
        console.error("Error fetching posts:", response.statusText);
        throw new Error("Failed to fetch posts");
      }

      // Parse the response data
      const data = await response.json();
      const newPosts: Post[] = data.data.children.map((post: any) => ({
        reddit_id: post.data.id,
        title: post.data.title,
        subreddit: post.data.subreddit,
        selftext: post.data.selftext,
        author: post.data.author,
        url: post.data.url,
        score: post.data.score,
        author_fullname: post.data.author_fullname,
        permalink: post.data.permalink,
      }));

      // Add the new posts to the existing posts array
      posts = [...posts, ...newPosts];
      // Update the after variable for pagination
      after = data.data.after;

      // Break the loop if there are no more pages to fetch
      if (!after) {
        break;
      }
    } catch (error) {
      console.error("Error fetching posts:", error);
      throw new Error("Failed to fetch posts");
    }
  }

  // Filter out existing submissions from the fetched posts
  const filteredPosts = await filterExistingSubmissions(posts);

  return filteredPosts;
}

// Function to filter out the submissions that already exist in the evaluated_submissions table
async function filterExistingSubmissions(posts: Post[]): Promise<Post[]> {
  try {
    // Fetch existing submissions
    const { data: existingSubmissions, error: fetchError } = await supabase
      .from("evaluated_submissions")
      .select("reddit_id, title")
      .in(
        "reddit_id",
        posts.map((post) => post.reddit_id)
      );

    if (fetchError) {
      console.error("Error fetching existing submissions:", fetchError);
      throw new Error(
        `Error fetching existing submissions: ${fetchError.message}`
      );
    }

    const existingRedditIds = new Set(
      existingSubmissions.map((s: { reddit_id: string }) => s.reddit_id)
    );
    const existingTitles = new Set(
      existingSubmissions.map((s: { title: string }) => s.title)
    );

    // Filter out submissions that already exist
    const newPosts = posts.filter((post) => {
      const isDuplicate =
        existingRedditIds.has(post.reddit_id) || existingTitles.has(post.title);
      if (isDuplicate) {
        console.log("Duplicate post:", post.title);
      } else {
        console.log("Unique post:", post.title);
      }
      return !isDuplicate;
    });

    return newPosts;
  } catch (error) {
    console.error("Error filtering existing submissions:", error);
    throw error;
  }
}
