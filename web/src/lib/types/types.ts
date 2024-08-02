// Interface for reddit post
export type Post = {
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
  isRelevant: boolean;
  reason: string;
  alignmentScore: number;
};

export type EvaluatedSubmission = {
  post: Post;
  isRelevant: boolean;
  reason: string;
  alignmentScore: number;
};
