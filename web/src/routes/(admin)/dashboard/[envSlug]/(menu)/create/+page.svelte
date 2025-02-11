<script lang="ts">
	import { Typography } from '$lib/components/ui/typography';
    import SetupForm from './setup-form.svelte';
    import type { SupabaseClient, Session } from '@supabase/supabase-js';

    let { data } = $props();

</script>

<div class="min-h-screen mt-16">
    <Typography variant="headline-lg" class="text-center">Create a new project</Typography>
    <Typography variant="body-md" class="text-center">
        As easy as providing your SaaS' URL.
    </Typography>
    <div class="w-full grid place-items-center">
        <SetupForm supabase={data.supabase} session={data.session} />
    </div>
</div>
