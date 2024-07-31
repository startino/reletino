import { fetchSubredditPosts } from "../../../redditClient/fetchSubredditPosts";
import { processPosts } from "../../../controllers/evaluation";

export const load = async () => {
  const result = await fetchSubredditPosts();
  const fetch = await processPosts();
  return { result, fetch };
};
