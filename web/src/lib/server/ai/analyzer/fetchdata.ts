import { supabase } from "$lib/supabase";

// Function to fetch data from evaluated_submissions
export async function fetchAgentSubmissions() {
  const { data } = await supabase
    .from("analyze_submissions")
    .select("*")
    .limit(10);

  console.log("Evaluated agent Data:", data);
  return data;
}
