import { supabase } from "$lib/supabase";
import { type TablesInsert } from "$lib/types/supabase";

// Function to save evaluated submissions
export async function saveEvaluatedSubmissions(
  submissions: TablesInsert<"evaluated_submissions">[]
) {
  try {
    console.log(`Attempting to process ${submissions.length} submissions`);
    if (submissions.length > 0) {
      console.log(
        "About to save the following Reddit IDs:",
        submissions.map((sub) => sub.reddit_id)
      );
      // Insert new submissions
      const { data, error } = await supabase
        .from("evaluated_submissions")
        .upsert(submissions, { onConflict: "title" })
        .select();
      if (error) {
        console.error("Supabase error details:", error);
        throw new Error(`Error saving new submissions: ${error.message}`);
      }
      console.log(`Successfully saved ${data.length} new submissions`);
      return data;
    } else {
      console.log("No new submissions to save.");
      return [];
    }
  } catch (error) {
    console.error("Error processing submissions:", error);
    throw error;
  }
}

// Function to save multiple leads
export async function saveLeads(leads: TablesInsert<"leads">[]) {
  try {
    const { data, error } = await supabase
      .from("leads")
      .upsert(leads, { onConflict: "reddit_id" });
    if (error) {
      console.error("Supabase error details:", error);
      throw new Error(`Error saving leads: ${error.message}`);
    }
    return data;
  } catch (error) {
    console.error("Error saving leads:", error);
    throw error;
  }
}
