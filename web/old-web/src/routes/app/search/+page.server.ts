import { fetchPostAndEvaluate } from "$lib/server/controllers/evaluation";

export const load = async () => {
  const fetch = await fetchPostAndEvaluate();
  return { fetch };
};
