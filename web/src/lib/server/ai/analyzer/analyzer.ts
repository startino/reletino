import { ChatOpenAI } from "@langchain/openai";
import { PromptTemplate } from "@langchain/core/prompts";
import { StructuredOutputParser } from "@langchain/core/output_parsers";
import { OPENAI_API_KEY } from "$env/static/private";
import { fetchAgentSubmissions, fetchHumanSubmissions } from "./fetchdata";
import { z } from "zod";

// Define the schema for the accuracy analysis
const accuracySchema = z.object({
  message: z
    .string()
    .describe("Analysis of accuracy and differences between submissions."),
});

// Create an instance of the output parser
const parser = StructuredOutputParser.fromZodSchema(accuracySchema);

export const accuracyAnalyzer = async (): Promise<string> => {
  // Fetch submissions
  const agentSubmission = await fetchAgentSubmissions();
  const humanSubmission = await fetchHumanSubmissions();

  // Initialize LLM
  const llm = new ChatOpenAI({
    model: "gpt-4",
    temperature: 0.1,
    apiKey: OPENAI_API_KEY,
  });

  // Create Prompt Template to compare submissions
  const prompt = new PromptTemplate({
    template: `
    As an expert data analyst, you are tasked with comparing the evaluation provided by the agent with the evaluation submitted the co-founder of Startino. Both evaluations assess the same posts, but the cofounder's evaluation focuses on relevance and reasons, and so does the agent's. Your objective is to check the accuracy of the agent’s evaluation by comparing it to the cofounder's. Specifically, you need to evaluate how well the relevance and reasons provided by the agent align with those provided by the cofounder. This involves checking if the agent’s relevance and reasons correctly match the cofounder's evaluation, determining if the agent’s evaluation is as comprehensive as the cofounder's, and assessing how well the agent’s relevance aligns with the cofounder's relevance in evaluating the posts. Here's the submissions evaluated by agent and the cofounder respectively.

    Agent's Submission:
    {agentSubmission}

    Cofounder's Submission:
    {humanSubmission}

    {format_instructions}`,
    inputVariables: ["agentSubmission", "humanSubmission"],
    partialVariables: { format_instructions: parser.getFormatInstructions() },
  });

  const chain = prompt.pipe(llm).pipe(parser);
  const result = await chain.invoke({ agentSubmission, humanSubmission });
  return result.message;
};
