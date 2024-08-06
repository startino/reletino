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
  alignment_score: number;
};

export type EvaluatedSubmission = {
  qualifying_question: string | null | undefined;
  post: Post;
  is_relevant: boolean;
  reason: string;
  alignment_score: number;
};
