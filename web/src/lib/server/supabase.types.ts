export type Json =
  | string
  | number
  | boolean
  | null
  | { [key: string]: Json | undefined }
  | Json[];

export type Database = {
  public: {
    Tables: {
      baptaTours: {
        Row: {
          created_at: string;
          email: string | null;
          firstName: string | null;
          id: number;
          lastName: string | null;
          message: string | null;
          people: number | null;
          tours: string | null;
          whatsapp: string | null;
        };
        Insert: {
          created_at?: string;
          email?: string | null;
          firstName?: string | null;
          id?: number;
          lastName?: string | null;
          message?: string | null;
          people?: number | null;
          tours?: string | null;
          whatsapp?: string | null;
        };
        Update: {
          created_at?: string;
          email?: string | null;
          firstName?: string | null;
          id?: number;
          lastName?: string | null;
          message?: string | null;
          people?: number | null;
          tours?: string | null;
          whatsapp?: string | null;
        };
        Relationships: [];
      };
      "Contact Forms": {
        Row: {
          companyName: string | null;
          created_at: string;
          email: string | null;
          id: number;
          message: string | null;
          name: string | null;
          phone: string | null;
          website: string | null;
        };
        Insert: {
          companyName?: string | null;
          created_at?: string;
          email?: string | null;
          id?: number;
          message?: string | null;
          name?: string | null;
          phone?: string | null;
          website?: string | null;
        };
        Update: {
          companyName?: string | null;
          created_at?: string;
          email?: string | null;
          id?: number;
          message?: string | null;
          name?: string | null;
          phone?: string | null;
          website?: string | null;
        };
        Relationships: [];
      };
      evaluated_submissions: {
        Row: {
          id: string;
          created_at: string;
          post_title: string;
          post_subreddit: string;
          post_selftext: string;
          post_author: string;
          post_url: string;
          post_score: number;
          post_author_fullname: string;
          post_permalink: string;
          is_relevant: boolean;
          reason: string;
          alignment_score: number;
        };
        Insert: {
          id?: string;
          created_at?: string;
          post_title: string;
          post_subreddit: string;
          post_selftext: string;
          post_author: string;
          post_url: string;
          post_score: number;
          post_author_fullname: string;
          post_permalink: string;
          is_relevant: boolean;
          reason: string;
          alignment_score: number;
        };
        Update: {
          id?: string;
          created_at?: string;
          post_title?: string;
          post_subreddit?: string;
          post_selftext?: string;
          post_author?: string;
          post_url?: string;
          post_score?: number;
          post_author_fullname?: string;
          post_permalink?: string;
          is_relevant?: boolean;
          reason?: string;
          alignment_score?: number;
        };
        Relationships: [];
      };
      leads: {
        Row: {
          comment: string | null;
          data: Json | null;
          discovered_at: string;
          id: string;
          last_contacted_at: string | null;
          last_event: string;
          prospect_name: string | null;
          prospect_username: string;
          reddit_id: string | null;
          source: string;
          status: string;
          submission_id: string | null;
        };
        Insert: {
          comment?: string | null;
          data?: Json | null;
          discovered_at?: string;
          id?: string;
          last_contacted_at?: string | null;
          last_event?: string;
          prospect_name?: string | null;
          prospect_username: string;
          reddit_id?: string | null;
          source?: string;
          status: string;
          submission_id?: string | null;
        };
        Update: {
          comment?: string | null;
          data?: Json | null;
          discovered_at?: string;
          id?: string;
          last_contacted_at?: string | null;
          last_event?: string;
          prospect_name?: string | null;
          prospect_username?: string;
          reddit_id?: string | null;
          source?: string;
          status?: string;
          submission_id?: string | null;
        };
        Relationships: [
          {
            foreignKeyName: "public_leads_submission_id_fkey";
            columns: ["submission_id"];
            isOneToOne: false;
            referencedRelation: "evaluated_submissions";
            referencedColumns: ["id"];
          },
        ];
      };
    };
    Views: {
      [_ in never]: never;
    };
    Functions: {
      [_ in never]: never;
    };
    Enums: {
      [_ in never]: never;
    };
    CompositeTypes: {
      [_ in never]: never;
    };
  };
};
