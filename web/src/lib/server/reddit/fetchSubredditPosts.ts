import { authenticate, userAgent } from "./authenticate";

interface Post {
  title: string;
  author: string;
  url: string;
  score: number;
  subreddit: string;
  selftext: string;
  author_fullname: string;
  permalink: string;
}

const SUBREDDIT_NAMES =
  "SaaS+SaaSy+startups+YoungEntrepreneurs+NoCodeSaas+nocode+cofounder+Entrepreneur+futino";

// Function to fetch posts from relevant subreddits
export async function fetchSubredditPosts(): Promise<Post[]> {
  console.log(`Fetching posts from subreddits: ${SUBREDDIT_NAMES}`);

  const url = `https://oauth.reddit.com/r/${SUBREDDIT_NAMES}/new.json`;

  const accessToken = await authenticate();

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

    const data = await response.json();
    console.log("Fetched posts data:", data);

    const posts: Post[] = data.data.children.map((post: any) => ({
      title: post.data.title,
      author: post.data.author,
      url: post.data.url,
      score: post.data.score,
      subreddit: post.data.subreddit,
      selftext: post.data.selftext,
      author_fullname: post.data.author_fullname,
      permalink: post.data.permalink,
    }));
    console.log("fetched: ", posts);
    return posts;
  } catch (error) {
    console.error("Error fetching posts:", error);
    throw new Error("Failed to fetch posts");
  }
}
