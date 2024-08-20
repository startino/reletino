import { supabase } from "$lib/supabase";
import { ChatOpenAI } from "@langchain/openai";
import { PromptTemplate } from "@langchain/core/prompts";
import { OPENAI_API_KEY } from "$env/static/private";
import { evaluateDataSetRelevance } from "./relevance";
import type { LabelledDataset, EvaluatedDataset } from "$lib/types/types";

import { StructuredOutputParser } from "@langchain/core/output_parsers";
import { z } from "zod";

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

const promptSchema = z.object({
  updatedPrompt: z
    .string()
    .describe("The updated prompt for evaluating posts more accurately."),
});

async function getPromptFromSupabase(): Promise<string | null> {
  console.log("Attempting to fetch prompt from Supabase...");

  const { data } = await supabase.from("prompt").select("prompt").single();

  if (!data || null) {
    console.error("No data");
    return null;
  }
  console.log("Fetched prompt from Supabase..");
  return data.prompt;
}

const updatePrompt = async (
  miscalculations: EvaluatedDataset[],
  currentPrompt: string | null
): Promise<string> => {
  const llm = new ChatOpenAI({
    model: "gpt-4o",
    temperature: 0.1,
    apiKey: OPENAI_API_KEY,
  });

  const parser = StructuredOutputParser.fromZodSchema(promptSchema);

  const prompt = new PromptTemplate({
    template:
      `You are a prompt engineer at startino. You need to improve the accuracy of the agent that checks whether the user who posted is a potential client for startino or not by evaluating the post. \n
      Right now its giving some miscalculations that is leading to potential clients being missed.  Here's the current prompt being used:\n\n` +
      `Current Prompt:\n{current_prompt}\n\n` +
      `And here are the miscalculations it made:\n{miscalculations}\n\n` +
      `Guidelines for the new prompt:
      1. Analyze the reasons of miscalculations and compare it with the company's context and modify the prompt.
      2. Make the prompt more detailed based on the company's context than the current one.` +
      `{format_instructions}\n\n` +
      `IMPORTANT: Provide only the updated prompt as a string in the JSON response. Do not include any other text or explanations.`,
    inputVariables: ["current_prompt", "miscalculations"],
    partialVariables: { format_instructions: parser.getFormatInstructions() },
  });

  const chain = prompt.pipe(llm).pipe(parser);

  const result = await chain.invoke({
    current_prompt: currentPrompt,
    miscalculations: JSON.stringify(miscalculations),
  });
  return result.updatedPrompt;
};

let currentPrompt = await getPromptFromSupabase();

export const promptImprover = async (): Promise<void> => {
  const sampleSize = 20;
  const requiredAccuracy = 0.8;
  let accuracy = 0;

  while (accuracy < requiredAccuracy) {
    const { data, error } = await supabase
      .from("labeled_dataset")
      .select("*")
      .limit(sampleSize);

    if (error || !data) {
      console.error("Error fetching labeled dataset:", error);
      return;
    }

    const miscalculations: EvaluatedDataset[] = [];
    let correctClassifications = 0;

    for (const post of data) {
      const dataset: LabelledDataset = { title: post.title, body: post.body };

      const evaluationResult = await evaluateDataSetRelevance(
        currentPrompt,
        dataset,
        "gpt-4o"
      );

      if (post.human_answer === evaluationResult.is_relevant) {
        correctClassifications++;
      } else {
        miscalculations.push(evaluationResult);
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
      await updatePromptInDatabase(newPrompt);
      currentPrompt = await getPromptFromSupabase();
    }
  }
  console.log(
    `Prompt improvement completed. Final accuracy: ${accuracy * 100}%`
  );
};
