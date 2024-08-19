import { ChatOpenAI } from "@langchain/openai";
import { PromptTemplate } from "@langchain/core/prompts";
import { StructuredOutputParser } from "@langchain/core/output_parsers";
import { z } from "zod";
import type { LabelledDataset } from "$lib/types/types";
import { OPENAI_API_KEY } from "$env/static/private";
import { supabase } from "$lib/supabase";

const dataSchema = z.object({
  message: z.string().describe("Post to be evaluated."),
});

export async function getPromptFromSupabase(): Promise<string | null> {
  console.log("Attempting to fetch prompt from Supabase...");

  const { data } = await supabase.from("prompt").select("prompt").single();

  if (!data) {
    console.error("NO data");
    return null;
  }

  return data.prompt;
}

export async function evaluateDataSetRelevance(
  post: LabelledDataset,
  modelName: string = "gpt-4o",
  currentPrompt: string
): Promise<string> {
  const llm = new ChatOpenAI({
    model: modelName,
    temperature: 0.1,
    apiKey: OPENAI_API_KEY,
  });

  console.log("Running evaluator with current prompt....");
  const parser = StructuredOutputParser.fromZodSchema(dataSchema);
  const prompt = new PromptTemplate({
    template:
      currentPrompt +
      `
    Now, evaluate the following post for alignment with the above context:
    {post}
    {format_instructions}
    
    Respond with a message of string indicating true or false if the post aligns with the context from the website.`,
    inputVariables: ["post"],
    partialVariables: { format_instructions: parser.getFormatInstructions() },
  });

  console.log("Evaluating post......");
  const chain = prompt.pipe(llm).pipe(parser);
  const result = await chain.invoke({ post: post.body });
  console.log("Evaluation result:", result.message);
  return result.message;
}
