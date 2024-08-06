import { processPosts } from "../../../lib/controllers/evaluation";

export const load = async () => {
  const fetch = await processPosts();
  return { fetch };
};
