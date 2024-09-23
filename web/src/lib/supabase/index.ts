import { createBrowserClient } from "$lib/supabase/clients"
import type {
  Database,
  Json,
  Tables,
  Enums,
} from "$lib/supabase/database.types"
export { createBrowserClient, createServerClient } from "$lib/supabase/clients"
export const supabase = createBrowserClient()

type Views = Database["public"]["Views"]
type Functions = Database["public"]["Functions"]
type CompositeTypes = Database["public"]["CompositeTypes"]

export type { Database, Tables, Enums, Views, Functions, CompositeTypes, Json }
