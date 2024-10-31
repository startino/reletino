<script lang="ts">
	import { getAuthState, getEnvironmentState } from '$lib/states';
	import { onMount } from 'svelte';

	const env = getEnvironmentState();
	const auth = getAuthState();
	const { data } = $props();

	onMount(() => {
		env.value = null;
		auth.user && (auth.user.is_anonymous = true);
	});
</script>

<svelte:head>
	<title>Current Password Incorrect</title>
</svelte:head>

<h1 class="mb-6 text-2xl font-bold">Current Password Incorrect</h1>

<p>You attempted edit your account with an incorrect current password, and have been logged out.</p>
<p class="mt-6">
	If you remember your password <a href="/login/sign_in" class="underline">sign in</a>
	and try again.
</p>
<p class="mt-6">
	If you forget your password <a href="/login/forgot_password" class="underline">reset it</a>
	.
</p>
