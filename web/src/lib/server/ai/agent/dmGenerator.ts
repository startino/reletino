import { ChatOpenAI } from "@langchain/openai";
import { PromptTemplate } from "@langchain/core/prompts";
import {
  JsonOutputParser,
  StructuredOutputParser,
} from "@langchain/core/output_parsers";
import { companyContext } from "../prompts/companyContext";
import type {
  Post,
  RelevanceResult,
  EvaluatedSubmission,
} from "$lib/types/types";
import { OPENAI_API_KEY } from "$env/static/private";
import { z } from "zod";
import { dmPrompt } from "../prompts/dmPrompt";

const dmSchema = z.object({
  message: z
    .string()
    .describe("Message to be sent to the lead acting as Jorge."),
});

// Generate a direct message
export const generateDM = async (post: Post): Promise<string> => {
  const llm = new ChatOpenAI({
    model: "gpt-4o",
    temperature: 0.1,
    apiKey: OPENAI_API_KEY,
  });

  const parser = StructuredOutputParser.fromZodSchema(dmSchema);

  const prompt = new PromptTemplate({
    template:
      dmPrompt +
      `
    COMPANY CONTEXT:` +
      companyContext +
      `Here is the post that the prospect posted:
    {post}
    
    {format_instructions}
    `,
    inputVariables: ["post"],
    partialVariables: { format_instructions: parser.getFormatInstructions() },
  });

  const chain = prompt.pipe(llm).pipe(parser);

  const result = await chain.invoke({ post });

  return result.message;
};
