import { promptImprover } from "$lib/server/ai/analyze/promptImprover";

export const load = async () => {
  const analyze = await promptImprover();
  return { analyze };
};
