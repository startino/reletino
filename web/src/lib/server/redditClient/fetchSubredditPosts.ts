import { supabase } from "$lib/supabase";
import { authenticate, userAgent } from "./authenticate";
import type { Post } from "$lib/types/types";

// List of subreddit names to fetch posts from
const SUBREDDIT_NAMES = "cofounder+startup+sass";

// Function to fetch posts from relevant subreddits
export async function fetchSubredditPosts(
  limit = 20, // Number of posts to fetch per page
  maxPages = 2 // Maximum number of pages to fetch
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

    //TODO come back here to clean up this code

    // Start

    // console.log(JSON.stringify(data, null, 2));
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

    // End

    // Add the new posts to the existing posts array
    posts = [...posts, ...newPosts];
    // Update the after variable for pagination
    after = data.data.after;

    // Break the loop if there are no more pages to fetch
    if (!after) {
      break;
    }
  }

  // Filter out existing submissions from the fetched posts
  const filteredPosts = await filterExistingSubmissions(posts);

  return filteredPosts;
}

// Function to filter out the submissions that already exist in the evaluated_submissions table
async function filterExistingSubmissions(posts: Post[]): Promise<Post[]> {
  // Fetch existing submissions
  const { data: existingSubmissions, error } = await supabase
    .from("evaluated_submissions")
    .select("reddit_id, title")
    .in(
      "reddit_id",
      posts.map((post) => post.reddit_id)
    );

  if (error || !existingSubmissions) {
    console.error("Error fetching existing submissions:", error);

    return [];

    // TODO: ask nazif is this is ok
    // throw new Error(`Error fetching existing submissions: ${error.message}`);
  }

  const existingRedditIds = existingSubmissions.map(
    (s: { reddit_id: string }) => s.reddit_id
  );
  const existingTitles = existingSubmissions.map(
    (s: { title: string }) => s.title
  );

  // Filter out submissions that already exist
  // TODO: Check for user's instead
  const newPosts = posts.filter((post) => {
    const isDuplicate =
      existingRedditIds.includes(post.reddit_id) ||
      existingTitles.includes(post.title);
    if (isDuplicate) {
      console.log("Duplicate post:", post.title);
    } else {
      console.log("Unique post:", post.title);
    }
    return !isDuplicate;
  });

  return newPosts;
}
