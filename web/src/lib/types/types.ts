// Interface for reddit post
export type Post = {
  reddit_id: string;
  title: string;
  author: string;
  url: string;
  score: number;
  subreddit: string;
  selftext: string;
  author_fullname: string;
  permalink: string;
};

export type RelevanceResult = {
  is_relevant: boolean;
  reason: string;
};

export type EvaluatedSubmission = {
  qualifying_question: string | null | undefined;
  post: Post;
  is_relevant: boolean;
  reason: string;
};

// Labelled dataset and evaluated post
// Updated types
export type LabelledDataset = {
  title: string;
  body: string;
};

export type DatasetRelevanceResult = {
  is_relevant: boolean;
  reason: string;
};

export type EvaluatedDataset = {
  dataset: LabelledDataset;
  is_relevant: boolean;
  reason: string;
};
