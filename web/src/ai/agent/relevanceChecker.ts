import { ChatOpenAI } from "@langchain/openai";
import { PromptTemplate } from "@langchain/core/prompts";
import { JsonOutputParser } from "@langchain/core/output_parsers";
import type {
  Post,
  RelevanceResult,
  EvaluatedSubmission,
} from "../../types/types";
import { relevancePrompt } from "../prompts/prompt";
import { PUBLIC_API_URL } from "$env/static/public";

// I am just assuming it
const tokenPrice = 0.0004;

// Dummy function to estimate token count
const estimateTokenCount = (text: string): number => {
  return text.split(/\s+/).length;
};

// Function to create a processing chain for evaluating the relevance of a post
async function createRelevanceChain(modelName: string) {
  const llm = new ChatOpenAI({
    model: modelName,
    temperature: 0.1,
    apiKey: PUBLIC_API_URL,
  });
  console.log("Creating Relevance Chain");
  const parser = new JsonOutputParser<RelevanceResult>();
  // Create a prompt template that includes our relevance context and instructions
  const prompt = new PromptTemplate({
    template: `${relevancePrompt}

Evaluate the following post for relevance:
{post}

{format_instructions}

Respond with a JSON object containing:
1. isRelevant: A boolean indicating if the post is relevant.
2. reason: A brief explanation of why the post is or isn't relevant.`,
    inputVariables: ["post"],
    partialVariables: { format_instructions: parser.getFormatInstructions() },
  });

  // Return a function that can be called to evaluate posts
  return async (input: { post: string }): Promise<RelevanceResult> => {
    const formattedPrompt = await prompt.format(input);
    const result = await llm.invoke(formattedPrompt);
    // console.log("Model Response:", result);

    const resultString: string = result.content as string;

    try {
      const parsedResult = parser.parse(resultString);
      return parsedResult;
    } catch (error) {
      console.error("Failed to parse JSON:", error);
      // console.log("Raw result string:", resultString);
      throw new Error("Failed to parse result as JSON");
    }
  };
}

// Function to invoke the chain and evaluate a post
async function invokeRelevanceChain(
  chain: (input: { post: string }) => Promise<RelevanceResult>,
  post: Post
): Promise<[RelevanceResult, number]> {
  // Retry logic: attempt to invoke the chain up to 3 times
  // console.log("invokeRelevanceChain");
  for (let i = 0; i < 3; i++) {
    // console.log(post.title);
    // console.log(post.selftext);
    try {
      const result = await chain({
        post: `Title: ${post.title}\nContent: ${post.selftext}`,
      });
      // Calculate token usage
      const promptText = `Title: ${post.title}\nContent: ${post.selftext}`;
      const numTokensInput = estimateTokenCount(promptText);
      const numTokensOutput = estimateTokenCount(JSON.stringify(result));
      const totalTokenCount = numTokensInput + numTokensOutput;
      const cost = totalTokenCount * tokenPrice;
      return [result, cost];
    } catch (error) {
      console.error(`An error occurred while invoking the chain: ${error}`);
      if (i === 2) throw new Error("Failed to invoke chain after 3 attempts.");
      await new Promise((resolve) => setTimeout(resolve, 5000)); // Wait 5 seconds before retrying
    }
  }
  throw new Error("This should never be reached due to the throw in the loop");
}

// Main function to evaluate post relevance
export async function evaluatePostRelevance(
  post: Post,
  modelName: string = "gpt-4"
): Promise<EvaluatedSubmission> {
  // console.log("evaluatePostRelevance");
  const chain = await createRelevanceChain(modelName);
  // Invoke the chain to get the relevance result
  const [result, cost] = await invokeRelevanceChain(chain, post);

  // Return the evaluated submission
  return { post, isRelevant: result.isRelevant, cost, reason: result.reason };
}
