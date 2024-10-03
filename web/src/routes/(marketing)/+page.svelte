<script lang="ts">
	import { WebsiteName, WebsiteBaseUrl, WebsiteDescription } from '$lib/config';
	import { Button, buttonVariants } from '$lib/components/ui/button';
	import * as Card from '$lib/components/ui/card';
	import { Typography } from '$lib/components/ui/typography';

	const ldJson = {
		'@context': 'https://schema.org',
		'@type': 'WebSite',
		name: WebsiteName,
		url: WebsiteBaseUrl,
	};
	const jsonldScript = `<script type="application/ld+json">${
		JSON.stringify(ldJson) + '<'
	}/script>`;
</script>

<svelte:head>
	<title>{WebsiteName}</title>
	<meta name="description" content={WebsiteDescription} />
	<!-- eslint-disable-next-line svelte/no-at-html-tags -->
	{@html jsonldScript}
</svelte:head>

<main class="relative">
	<div
		class="absolute inset-2 bottom-0 rounded-3xl ring-1 ring-inset ring-black/5 bg-[linear-gradient(115deg,var(--tw-gradient-stops))] from-tertiary from-[28%] via-secondary to-primary sm:bg-[linear-gradient(145deg,var(--tw-gradient-stops))]"
	></div>
	<div
		class="px-12 lg:px-24 py-44 lg:pb-12 flex flex-col text-primary-foreground rounded-3xl text-start relative place-items-start"
	>
		<div class="">
			<Typography
				class="text-balance text-6xl/[0.9] font-medium tracking-tight text-start sm:text-8xl/[0.8] md:text-9xl/[0.8]"
			>
				Close every deal.
			</Typography>
			<Typography
				variant="title-md"
				class="text-balance pt-8 max-w-lg text-xl/7 font-medium 5 sm:text-2xl/8 text-start"
			>
				Reletino helps you sell more by revealing leads from Reddit, through an AI Agent.
			</Typography>
		</div>
		<div class="flex flex-col gap-6 mt-12 gap-x-6 gap-y-4 sm:flex-row">
			<Button
				href="/onboarding"
				class="w-full bg-background text-foreground rounded-3xl hover:bg-background/80"
				size="lg"
			>
				Get Started
			</Button>
			<!-- <Button
        href="#demo-video"
        class="w-full bg-background text-background rounded-3xl bg-foreground/40 border-2 border-foreground/50 hover:bg-foreground/60 font-semibold"
        variant="outline"
        size="lg"
      >
        Learn More
      </Button>  -->
		</div>
		<Typography variant="body-md" class="pt-24 text-start">
			*Reletino is in Beta, credits are free for early users.
		</Typography>
	</div>
</main>
