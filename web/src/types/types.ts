// Interface for reddit post
export interface Post {
  title: string;
  author: string;
  url: string;
  score: number;
  subreddit: string;
  selftext: string;
  author_fullname: string;
  permalink: string;
}

export interface RelevanceResult {
  isRelevant: boolean;
  reason: string;
}

export interface EvaluatedSubmission {
  post: Post;
  isRelevant: boolean;
  cost: number;
  reason: string;
}
