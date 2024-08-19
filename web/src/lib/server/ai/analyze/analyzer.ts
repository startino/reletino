import { supabase } from "$lib/supabase";
import { ChatOpenAI } from "@langchain/openai";
import { PromptTemplate } from "@langchain/core/prompts";
import { OPENAI_API_KEY } from "$env/static/private";
import { evaluateDataSetRelevance, getPromptFromSupabase } from "./relevance";
import type { evaluatedPostType } from "$lib/types/types";
import { z } from "zod";
import { StructuredOutputParser } from "@langchain/core/output_parsers";

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
  miscalculations: evaluatedPostType[],
  currentPrompt: string
): Promise<string> => {
  const llm = new ChatOpenAI({
    model: "gpt-4o",
    temperature: 0.1,
    apiKey: OPENAI_API_KEY,
  });

  const zodSchema = z.object({
    updatedPrompt: z
      .string()
      .describe("The updated prompt based on analysis of misclassifications"),
  });

  const parser = StructuredOutputParser.fromZodSchema(zodSchema);

  const prompt = new PromptTemplate({
    template:
      `You are a prompt engineer at startino. You need to improve the accuracy of the agent that checks either the user that posted it is potential client for startino or not by evaluating the post. Right now its giving some misculcations that leads to potential client being missed. Now being a prompt engineer you need to update the existing prompt of the evaluator so that it evaluates the post more accurately based on the startino's context. Here's the current prompt being used:\n\n` +
      `Current Prompt:\n{current_prompt}\n\n` +
      `And here's the miscalculations it did:\n{miscalculations}\n\n` +
      `\n\n` +
      `{format_instructions}`,
    inputVariables: ["current_prompt", "miscalculations"],
    partialVariables: { format_instructions: parser.getFormatInstructions() },
  });

  const chain = prompt.pipe(llm).pipe(parser);

  const result = await chain.invoke({
    current_prompt: currentPrompt,
    miscalculations,
  });
  console.log("New prompt generated.....");
  return result.updatedPrompt;
};

export const promptImprover = async (): Promise<void> => {
  const sampleSize = 15;
  const requiredAccuracy = 0.9;
  let accuracy = 0;
  let currentPrompt = await getPromptFromSupabase();

  if (!currentPrompt) {
    console.error("Failed to fetch initial prompt from Supabase");
    return;
  }

  while (accuracy < requiredAccuracy) {
    const { data, error } = await supabase
      .from("labeled_dataset")
      .select("*")
      .limit(sampleSize);

    if (error || !data) {
      console.error("Error fetching labeled dataset:", error);
      return;
    }

    const miscalculations: evaluatedPostType[] = [];
    let correctClassifications = 0;

    for (const post of data) {
      const agentAnswer = await evaluateDataSetRelevance(
        { body: post.body },
        "gpt-4o",
        currentPrompt
      );
      if (post.human_answer.toString() === agentAnswer) {
        correctClassifications++;
      } else {
        miscalculations.push({
          body: post.body,
          human_answer: post.human_answer,
          agent_answer: agentAnswer,
        });
      }
    }

    accuracy = correctClassifications / sampleSize;
    console.log(`Accuracy: ${accuracy * 100}%`);

    if (accuracy >= requiredAccuracy) {
      console.log(
        "Achieved required accuracy. Stopping the improvement process."
      );
      break;
    }

    console.log(
      `Evaluated ${sampleSize} posts. ${miscalculations.length} were misclassified.`
    );

    if (miscalculations.length > 0) {
      const newPrompt = await updatePrompt(miscalculations, currentPrompt);
      console.log("Updated prompt:");
      console.log(newPrompt.substring(0, 100) + "...");
      await updatePromptInDatabase(newPrompt);
      currentPrompt = newPrompt;
    }
  }
  console.log(
    `Prompt improvement completed. Final accuracy: ${accuracy * 100}%`
  );
};
