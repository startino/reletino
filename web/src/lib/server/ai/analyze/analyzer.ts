import { supabase } from "$lib/supabase";
import { ChatOpenAI } from "@langchain/openai";
import { ChatPromptTemplate } from "@langchain/core/prompts";
import { OPENAI_API_KEY } from "$env/static/private";
import { evaluateDataSetRelevance } from "./relevance";
import type { evaluatedPostType } from "$lib/types/types";
import { relevancePrompt } from "../prompts/relevancePrompt";
import { companyContext } from "../prompts/companyContext";

const updatePrompt = async (
  incorrectEvaluations: evaluatedPostType[],
  miscalculations: any
): Promise<string> => {
  const llm = new ChatOpenAI({
    model: "gpt-4o",
    temperature: 0.1,
    apiKey: OPENAI_API_KEY,
  });

  const prompt = ChatPromptTemplate.fromTemplate(
    `
    Current prompt:
    ${relevancePrompt}

    Company context:
    ${companyContext}

    The current prompt is resulting in these misclassifications:
    ${miscalculations}
    ` +
      `Please provide an updated prompt that would help correctly classify these posts and similar ones in the future.`
  );

  const result = await llm.invoke(await prompt.formatMessages({}));
  return result.content as string;
};

export const promptImprover = async (): Promise<void> => {
  // Fetch data
  const { data, error } = await supabase
    .from("labeled_dataset")
    .select("*")
    .limit(10);
  if (error || !data) {
    console.error("Error fetching labeled dataset:", error);
    return;
  }

  // Evaluate posts and identify incorrect classifications
  const incorrectEvaluations: evaluatedPostType[] = [];
  for (const post of data) {
    const agentAnswer = await evaluateDataSetRelevance(
      { body: post.body },
      "gpt-4o"
    );
    if (post.human_answer.toString() !== agentAnswer) {
      incorrectEvaluations.push({
        body: post.body,
        human_answer: post.human_answer,
        agent_answer: agentAnswer,
      });
    }
  }

  // Log results
  console.log(
    `Evaluated ${data.length} posts. ${incorrectEvaluations.length} were misclassified.`
  );

  // Update prompt if there were misclassifications
  if (incorrectEvaluations.length > 0) {
    const miscalculations = incorrectEvaluations.map(
      (evaluated) =>
        `Post: ${evaluated.body}
       Human classification: ${evaluated.human_answer}
       Agent classification: ${evaluated.agent_answer}`
    );
    const newPrompt = await updatePrompt(incorrectEvaluations, miscalculations);
    console.log("Updated prompt:");
    console.log(newPrompt);
  } else {
    console.log("No misclassifications. Current prompt is performing well.");
  }
};
