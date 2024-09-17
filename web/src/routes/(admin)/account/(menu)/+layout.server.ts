import { redirect } from '@sveltejs/kit'
import type { LayoutServerLoad } from './$types'
import type { Tables } from '$lib/supabase';

export const load: LayoutServerLoad = async ({ locals: { supabase, safeGetSession, user }, cookies }) => {

    if (!user) {
        redirect(303, "/login")
    }

    const { data: usage, error: eUsage } = await supabase.from("usage").select("*").eq("profile_id", user.id).single()

    if (eUsage || !usage) {
        console.error("Error loading credits:", eUsage)
        return { status: 500, error: new Error("Failed to load credits") }
    }

    return {
        usage: usage as Tables<"usage">
    }
}