import { promptImprover } from "$lib/server/ai/analyze/analyzer";

export const load = async () => {
  const analyze = await promptImprover();
  return { analyze };
};
