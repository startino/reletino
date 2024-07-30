import { authenticate, userAgent } from "./authenticate";
import { type Post } from "../types/types";

// List of subreddit names to fetch posts from
const SUBREDDIT_NAMES =
  "SaaS+SaaSy+startups+YoungEntrepreneurs+NoCodeSaas+nocode+cofounder+Entrepreneur+futino";

// Function to fetch posts from relevant subreddits
export async function fetchSubredditPosts(
  limit = 25, // Number of posts to fetch per page
  maxPages = 5 // Maximum number of pages to fetch
): Promise<Post[]> {
  console.log(`Fetching posts from subreddits: ${SUBREDDIT_NAMES}`);

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
      console.log("Fetched posts data:", data);

      const newPosts: Post[] = data.data.children.map((post: any) => ({
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

  // console.log("Fetched all posts:", posts);
  // Go to localhost:5173/app/search to see the fetched data in the frontend
  return posts;
}
