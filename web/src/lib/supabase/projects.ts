import type { SupabaseClient } from '@supabase/supabase-js';
import type { Database } from './database.types';

export const deleteProject = async (
	id: string,
	{ supabase }: { supabase: SupabaseClient<Database> }
) => await supabase.from('projects').delete().eq('id', id);
