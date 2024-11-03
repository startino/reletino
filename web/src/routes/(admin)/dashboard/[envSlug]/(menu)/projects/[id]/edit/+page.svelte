<script lang="ts">
	import { Typography } from '$lib/components/ui/typography';
	import ProjectForm from './project-form.svelte';

	let { data } = $props();

	let { supabase, environment, project: _project } = data;

	let project = $state(_project);
</script>

<div class="mx-auto max-w-3xl">
	<Typography as="h1" variant="headline-sm" class="mb-4">Edit Project</Typography>
	<ProjectForm {supabase} {environment} projectForm={data.projectForm} bind:project />
</div>
