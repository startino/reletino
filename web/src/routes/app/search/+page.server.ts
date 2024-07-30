import { fetchSubredditPosts } from "../../../api/fetchSubredditPosts";

export const load = async () => {
  const result = await fetchSubredditPosts();
  return { result };
};
