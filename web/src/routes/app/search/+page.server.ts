import { fetchSubredditPosts } from "$lib/server/reddit/fetchSubredditPosts";

export const load = async () => {
  const result = await fetchSubredditPosts();
  return { result };
};
