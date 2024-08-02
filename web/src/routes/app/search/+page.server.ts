import { fetchSubredditPosts } from "$lib/redditClient/fetchSubredditPosts";
import { processPosts } from "../../../lib/controllers/evaluation";

export const load = async () => {
  const result = await fetchSubredditPosts();
  const fetch = await processPosts();
  return { result, fetch };
};
