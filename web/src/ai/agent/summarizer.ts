import { ChatOpenAI } from "@langchain/openai";
import { type Post } from "../../types/types";
import { companyContext } from "../prompts/prompt";
import { PUBLIC_API_URL } from "$env/static/public";

// Dummy functions to mimic behavior in the absence of actual implementations
const trim = (text: string): string => {
  return text.trim();
};

const getNumTokens = (text: string): number => {
  return text.split(/\s+/).length;
};

const tokenPrice = 0.0004;

// Implement the summarizePost function
export async function summarizePost(post: Post): Promise<Post> {
  // Initialize the OpenAI model
  try {
    const llm = new ChatOpenAI({
      model: "gpt-4",
      temperature: 0,
      apiKey: PUBLIC_API_URL,
    });
    let selftext = trim(post.selftext);

    if (getNumTokens(selftext) < 150) {
      return post;
    }

    const purpose = "Find potential clients and leads."; // Replace with actual purpose

    // Define the template for the summarization
    const template = `
      # Welcome Summary Writer!
      Your job is to help a Virtual Assistant in filtering Reddit posts.
      You'll help by summarizing the content of a Reddit post to remove any useless parts.
  
      # Guidelines
      - Extract information from each sentence and include it in the summary.
      - Use bullet points to list the main points.
      - DO NOT remove any crucial information.
      - IF PRESENT, you must include information about the author such as his profession (or student) and if he knows how to code.
      - DO NOT make up any information that was not present in the original text.
      - Commendations and encouragements should be removed.
  
      # Body Text To Summarize
      \`\`\`
      ${selftext}
      \`\`\`
  
      # Here is more information for context
      ${companyContext}
  
      ## Purpose of this process
      ${purpose}
    `;

    // Invoke the summarization model
    const summaryResult = await llm.invoke(template);
    const summarizedSelftext = JSON.stringify(summaryResult.content);

    // Calculate token usage
    const preTokenCount = getNumTokens(selftext);
    const postTokenCount = getNumTokens(summarizedSelftext);
    const tokenUsage = preTokenCount + postTokenCount; // Total tokens used

    // Calculate monetary cost
    const cost = tokenUsage * tokenPrice;

    // Print the token reduction and cost
    const reduction = ((preTokenCount - postTokenCount) / preTokenCount) * 100;
    console.log(`Post Summarization Results:`);
    console.log(`----------------------------------`);
    console.log(`Original text token count: ${preTokenCount}`);
    console.log(`Summarized text token count: ${postTokenCount}`);
    console.log(`Token reduction: ${reduction.toFixed(3)}%`);
    console.log(`Estimated cost: $${cost.toFixed(4)}`);
    console.log(`----------------------------------`);

    // Update the post object with the summarized content
    post.selftext = summarizedSelftext;

    return post;
  } catch (error) {
    console.error("Error summarizing post:", error);
    throw new Error("Failed to summarize the post");
  }
}
