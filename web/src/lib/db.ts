import { supabase } from "./supabase";
import type { TablesInsert } from "./types/supabase";

// Function to filter out the submissions and save it in lead
export async function saveEvaluatedSubmissions(
  submissions: TablesInsert<"evaluated_submissions">[]
) {
  try {
    console.log(`Attempting to process ${submissions.length} submissions`);
    // Fetch existing submissions
    const { data: existingSubmissions, error: fetchError } = await supabase
      .from("evaluated_submissions")
      .select("reddit_id, title")
      .in(
        "reddit_id",
        submissions.map((s) => s.reddit_id)
      );
    if (fetchError) {
      console.error("Error fetching existing submissions:", fetchError);
      throw new Error(
        `Error fetching existing submissions: ${fetchError.message}`
      );
    }
    const existingRedditIds = new Set(
      existingSubmissions.map((s) => s.reddit_id)
    );
    const existingTitles = new Set(existingSubmissions.map((s) => s.title));
    console.log(
      "Number of existing submissions found:",
      existingSubmissions.length
    );
    // Filter out submissions that already exist
    const newSubmissions = submissions.filter(
      (submission) =>
        !existingRedditIds.has(submission.reddit_id) &&
        !existingTitles.has(submission.title)
    );
    console.log(`Filtered down to ${newSubmissions.length} new submissions`);
    if (newSubmissions.length > 0) {
      console.log(
        "About to save the following Reddit IDs:",
        newSubmissions.map((sub) => sub.reddit_id)
      );
      // Insert new submissions
      const { data, error } = await supabase
        .from("evaluated_submissions")
        .insert(newSubmissions)
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
