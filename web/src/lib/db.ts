import { supabase } from "./supabase";
import type { TablesInsert } from "./types/supabase";

export async function saveEvaluatedPosts(
  evaluatedPosts: TablesInsert<"evaluated_submissions">[]
): Promise<void> {
  try {
    console.log(
      "Attempting to insert/update posts. Count:",
      evaluatedPosts.length
    );

    const { data, error } = await supabase
      .from("evaluated_submissions")
      .upsert(evaluatedPosts);

    if (error) {
      console.error("Supabase error details:", error);
      throw new Error(`Error inserting/updating posts: ${error.message}`);
    }
  } catch (error) {
    console.error("Error saving evaluated posts:", error);
    throw error;
  }
}
