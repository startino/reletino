import { ChatOpenAI } from "@langchain/openai";
import { ChatPromptTemplate } from "@langchain/core/prompts";
import { JsonOutputParser } from "@langchain/core/output_parsers";
import { OPENAI_API_KEY } from "$env/static/private";

import type {
  LabelledDataset,
  EvaluatedDataset,
  DatasetRelevanceResult,
} from "$lib/types/types";

export async function evaluateDataSetRelevance(
  currentPrompt: string | null,
  dataset: LabelledDataset,
  modelName: string = "gpt-4o"
): Promise<EvaluatedDataset> {
  const llm = new ChatOpenAI({
    model: modelName,
    temperature: 0.1,
    apiKey: OPENAI_API_KEY,
  });

  const parser = new JsonOutputParser<DatasetRelevanceResult>();

  const promptTemplate = ChatPromptTemplate.fromTemplate(`
    ${currentPrompt}
    Now, evaluate the following post for alignment with the above context:
    {dataset}
    {format_instructions}

    Respond with a valid JSON object containing:
    - is_relevant: A boolean indicating if the post aligns with the context from the website.
    - reason: A brief reason for the post being relevant or not.
  `);

  const formattedPrompt = await promptTemplate.partial({
    format_instructions: parser.getFormatInstructions(),
  });

  const chain = formattedPrompt.pipe(llm).pipe(parser);

  const result = await chain.invoke({
    dataset: `Title: ${dataset.title}\nContent: ${dataset.body}`,
  });

  return {
    dataset,
    is_relevant: result.is_relevant,
    reason: result.reason,
  };
}
