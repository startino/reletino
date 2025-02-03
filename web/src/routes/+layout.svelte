<script lang="ts">
	import '../app.css';
	import { navigating } from '$app/stores';
	import { expoOut } from 'svelte/easing';
	import { slide } from 'svelte/transition';
	import { Toaster } from '$lib/components/ui/sonner';

	import { setEnvironmentState, setAuthState } from '$lib/states';
	import { onMount } from 'svelte';
	import { goto, invalidate } from '$app/navigation';

	let { children, data } = $props();

	const envState = setEnvironmentState(data.environment);
	const authState = setAuthState(data.auth);

	$effect(() => {
		envState.value = data.environment;
		setAuthState(data.auth);
	});

	onMount(() => {
		data.supabase.auth.onAuthStateChange(async (event, session) => {
			// Redirect to account after successful login
			if (event == 'SIGNED_IN') {
				await invalidate('data:init');

				const freshLogin = session?.access_token !== authState.session?.access_token;

				authState.session = session;
				authState.user = session ? session.user : null;
				// Delay needed because order of callback not guaranteed.
				// Give the layout callback priority to update state or
				// we'll just bounch back to login when /account tries to load
				if (session?.user.is_anonymous) {
					return;
				}
				if (!freshLogin) {
					return;
				}
				setTimeout(() => {
					goto('/find-env');
				}, 200);
			}
		});
	});
</script>

{#if $navigating}
	<!-- 
    Loading animation for next page since svelte doesn't show any indicator. 
     - delay 100ms because most page loads are instant, and we don't want to flash 
     - long 12s duration because we don't actually know how long it will take
     - exponential easing so fast loads (>100ms and <1s) still see enough progress,
       while slow networks see it moving for a full 12 seconds
  -->
	<div
		class="bg-primary fixed left-0 right-0 top-0 z-50 h-1 w-full"
		in:slide={{ delay: 100, duration: 12000, axis: 'x', easing: expoOut }}
	></div>
{/if}

<Toaster position="bottom-left" richColors />

<div class="bg-background text-foreground">
	{@render children()}
</div>
