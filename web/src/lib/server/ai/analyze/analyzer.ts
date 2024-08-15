import { supabase } from "$lib/supabase";
import { ChatOpenAI } from "@langchain/openai";
import { ChatPromptTemplate } from "@langchain/core/prompts";
import { OPENAI_API_KEY } from "$env/static/private";
import { evaluateDataSetRelevance, supabasePrompt } from "./relevance";
import type { evaluatedPostType } from "$lib/types/types";

const updatePromptInDatabase = async (prompt: string): Promise<void> => {
  const { error } = await supabase
    .from("prompt")
    .update({ prompt })
    .eq("id", 1);

  if (error) {
    console.error("Error updating prompt in Supabase:", error);
  } else {
    console.log("Prompt successfully updated in the database.");
  }
};

const updatePrompt = async (
  miscalculations: evaluatedPostType[]
): Promise<string> => {
  const llm = new ChatOpenAI({
    model: "gpt-4o",
    temperature: 0.1,
    apiKey: OPENAI_API_KEY,
  });

  const prompt = ChatPromptTemplate.fromTemplate(
    `
    You are an AI prompt engineering expert. Your task is to improve a prompt used for classifying posts as relevant or not relevant to a specific company context.` +
      `Here's the prompt that is being used:` +
      { supabasePrompt } +
      `The current prompt is resulting in these misclassifications:
    ${miscalculations}

    Based on these misclassifications, please generate a update the existing prompt that addresses the following:
    1. Incorporate specific elements from the company context that are crucial for determining relevance.
    2. Add clear instructions on how to handle edge cases or ambiguous posts.
    3. Include examples of relevant and irrelevant posts based on the misclassifications.
    4. Provide a step-by-step approach for evaluating post relevance.

    Your new prompt should be significantly different from the current one and should aim to correctly classify the misclassified posts as well as similar cases in the future. You should provide only prompt nothing more.
`
  );

  const result = await llm.invoke(await prompt.formatMessages({}));
  return result.content as string;
};

export const promptImprover = async (): Promise<void> => {
  // Fetch data
  const { data, error } = await supabase
    .from("labeled_dataset")
    .select("*")
    .limit(2);
  if (error || !data) {
    console.error("Error fetching labeled dataset:", error);
    return;
  }

  // Evaluate posts and identify incorrect classifications
  const miscalculations: evaluatedPostType[] = [];

  for (const post of data) {
    const agentAnswer = await evaluateDataSetRelevance(
      { body: post.body },
      "gpt-4o"
    );
    if (post.human_answer.toString() !== agentAnswer) {
      miscalculations.push({
        body: post.body,
        human_answer: post.human_answer,
        agent_answer: agentAnswer,
      });
    }
  }

  // Log results
  console.log(
    `Evaluated ${data.length} posts. ${miscalculations.length} were misclassified.`
  );

  if (miscalculations.length > 0) {
    const newPrompt = await updatePrompt(miscalculations);
    console.log("Updated prompt:");
    console.log(newPrompt);

    // Update the new prompt in the database
    await updatePromptInDatabase(newPrompt);
  } else {
    console.log("No misclassifications. Current prompt is performing well.");
  }
};
