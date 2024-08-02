import { ChatOpenAI } from "@langchain/openai";
import { OpenAIEmbeddings } from "@langchain/openai";
import { CheerioWebBaseLoader } from "@langchain/community/document_loaders/web/cheerio";
import { RecursiveCharacterTextSplitter } from "langchain/text_splitter";
import { MemoryVectorStore } from "langchain/vectorstores/memory"; // Consider changing to a more robust vector store
import { PromptTemplate } from "@langchain/core/prompts";
import { JsonOutputParser } from "@langchain/core/output_parsers";
import { companyContext, relevancePrompt } from "../prompts/prompt";

import type {
  Post,
  RelevanceResult,
  EvaluatedSubmission,
} from "../../types/types";
import { PUBLIC_API_URL } from "$env/static/public";
import type { Document } from "@langchain/core/documents";

// Load and process documents
async function loadAndProcessDocuments() {
  console.log("Loading and processing documents for RAG model...");
  const urls = ["https://starti.no"];
  const loaders = urls.map((url) => new CheerioWebBaseLoader(url));
  const docs = await Promise.all(loaders.map((loader) => loader.load()));
  const flatDocs = docs.flat();

  const textSplitter = new RecursiveCharacterTextSplitter({
    chunkSize: 500,
    chunkOverlap: 0,
  });

  const splitDocs = await textSplitter.splitDocuments(flatDocs);
  console.log("Loaded and split documents into chunks");
  return splitDocs;
}

// Create a vector store from documents
async function createVectorStore(documents: Document<Record<string, any>>[]) {
  console.log("Creating vector store for RAG model...");
  const embeddings = new OpenAIEmbeddings({
    apiKey: PUBLIC_API_URL,
  });
  const vectorStore = await MemoryVectorStore.fromDocuments(
    documents,
    embeddings
  );
  console.log("Vector store created successfully");
  return vectorStore;
}

// Create a relevance chain
async function createRelevanceChain(
  modelName: string,
  vectorStore: MemoryVectorStore
) {
  console.log("Creating relevance chain with RAG model...");
  const llm = new ChatOpenAI({
    model: modelName,
    temperature: 0.1,
    apiKey: PUBLIC_API_URL,
  });

  const parser = new JsonOutputParser<RelevanceResult>();
  const retriever = vectorStore.asRetriever();

  const prompt = new PromptTemplate({
    template: `
    ${relevancePrompt}
    Here is the relevant context from the website:
    ${companyContext}
    {context}
    
    Now, evaluate the following Reddit post for alignment with the above context:
    {post}
    
    {format_instructions}
    
    Respond with a JSON object containing:
    1. isRelevant: A boolean indicating if the post aligns with the context from the website.
    2. reason: A detailed explanation of why the post does or doesn't align, citing specific examples from both the post and the context.
    3. alignmentScore: A number between 0 and 5 indicating how closely the post aligns with the context (0 being not at all, 5 being perfect alignment).`,
    inputVariables: ["context", "post"],
    partialVariables: { format_instructions: parser.getFormatInstructions() },
  });

  return async (input: { post: string }): Promise<RelevanceResult> => {
    console.log("Retrieving relevant documents for input...");
    const relevantDocs = await retriever.invoke(input.post); // Retrieve documents based on semantic similarity
    const context = relevantDocs.map((doc) => doc.pageContent).join("\n\n");

    const formattedPrompt = await prompt.format({ ...input, context });
    const result = await llm.invoke(formattedPrompt);
    const resultString: string = result.content as string;

    try {
      return parser.parse(resultString);
    } catch (error) {
      console.error("Failed to parse JSON:", error);
      throw new Error("Failed to parse result as JSON");
    }
  };
}

// Invoke the relevance chain with retries
async function invokeRelevanceChain(
  chain: (input: { post: string }) => Promise<RelevanceResult>,
  post: Post
): Promise<RelevanceResult> {
  for (let i = 0; i < 3; i++) {
    try {
      const postContent = `Title: ${post.title}\nContent: ${post.selftext}`;
      return await chain({ post: postContent });
    } catch (error) {
      console.error(`An error occurred while invoking the chain: ${error}`);
      if (i === 2) throw new Error("Failed to invoke chain after 3 attempts.");
      console.log(`Retrying in 5 seconds... (Attempt ${i + 2} of 3)`);
      await new Promise((resolve) => setTimeout(resolve, 5000));
    }
  }
  throw new Error("This should never be reached due to the throw in the loop");
}

let vectorStore: MemoryVectorStore | null = null;

// Initialize vector store if not already done
async function initializeVectorStore() {
  if (!vectorStore) {
    console.log("Initializing vector store for RAG model...");
    const documents = await loadAndProcessDocuments();
    vectorStore = await createVectorStore(documents);
    console.log("Vector store initialized successfully");
  }
  return vectorStore;
}

// Evaluate post relevance
export async function evaluatePostRelevance(
  post: Post,
  modelName: string = "gpt-4"
): Promise<EvaluatedSubmission> {
  console.log(`Evaluating post relevance using RAG model: ${post.title}`);
  const store = await initializeVectorStore();
  const chain = await createRelevanceChain(modelName, store);

  const result = await invokeRelevanceChain(chain, post);

  console.log(
    `Relevance: ${result.isRelevant}, Alignment Score: ${result.alignmentScore}`
  );

  return {
    post,
    isRelevant: result.isRelevant,
    reason: result.reason,
    alignmentScore: result.alignmentScore,
  };
}
