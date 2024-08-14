import { ChatOpenAI } from "@langchain/openai";
import { PromptTemplate } from "@langchain/core/prompts";
import { JsonOutputParser } from "@langchain/core/output_parsers";
import { companyContext } from "../prompts/companyContext";
import { relevancePrompt } from "../prompts/relevancePrompt";

import type {
  Post,
  EvaluatedSubmission,
  RelevanceResult,
} from "$lib/types/types";
import { OPENAI_API_KEY } from "$env/static/private";

export async function evaluatePostRelevance(
  post: Post,
  modelName: string = "gpt-4o"
): Promise<EvaluatedSubmission> {
  const llm = new ChatOpenAI({
    model: modelName,
    temperature: 0.1,
    apiKey: OPENAI_API_KEY,
  });

  const parser = new JsonOutputParser<RelevanceResult>();

  const prompt = new PromptTemplate({
    template: `
    {relevancePrompt} 
    Here is the context for the company: 

    {companyContext} 
    Now, evaluate the following Reddit post for alignment with the above context:
    {post}
    {format_instructions}
    
    Respond with a JSON object containing:
    1. is_relevant: A boolean indicating if the post aligns with the context from the website.
    2. reason: A detailed explanation of why the post does or doesn't align, citing specific examples from both the post and the context.`,
    inputVariables: ["post"],
    partialVariables: { format_instructions: parser.getFormatInstructions() },
  });

  const formattedPrompt = await prompt.format({
    post: `Title: ${post.title}\nContent: ${post.selftext}`,
    companyContext,
    relevancePrompt,
  });

  const result = await llm.invoke(formattedPrompt);
  const resultString = JSON.stringify(result.content);
  const relevanceResult = await parser.parse(resultString);

  return {
    post,
    qualifying_question: null,
    is_relevant: relevanceResult.is_relevant,
    reason: relevanceResult.reason,
  };
}
