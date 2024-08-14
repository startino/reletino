import { ChatOpenAI } from "@langchain/openai";
import { PromptTemplate } from "@langchain/core/prompts";
import { StructuredOutputParser } from "@langchain/core/output_parsers";
import { companyContext } from "../prompts/companyContext";
import { relevancePrompt } from "../prompts/relevancePrompt";
import { z } from "zod";
import type { LabelledDataset } from "$lib/types/types";
import { OPENAI_API_KEY } from "$env/static/private";

const dataSchema = z.object({
  message: z.string().describe("Post to be evaluated."),
});

export async function evaluateDataSetRelevance(
  post: LabelledDataset,
  modelName: string = "gpt-4o"
): Promise<string> {
  const llm = new ChatOpenAI({
    model: modelName,
    temperature: 0.1,
    apiKey: OPENAI_API_KEY,
  });

  const parser = StructuredOutputParser.fromZodSchema(dataSchema);

  const prompt = new PromptTemplate({
    template:
      { relevancePrompt } +
      `
    Here is the context for the company: 
 ` +
      { companyContext } +
      `
    Now, evaluate the following post for alignment with the above context:
    {post}
    {format_instructions}
    
    Respond with a message of boolean indicating if the post aligns with the context from the website.`,
    inputVariables: ["post"],
    partialVariables: { format_instructions: parser.getFormatInstructions() },
  });

  const chain = prompt.pipe(llm).pipe(parser);
  const result = await chain.invoke({ post: post.body });
  return result.message;
}
