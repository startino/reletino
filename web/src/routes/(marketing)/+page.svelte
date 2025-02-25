<script lang="ts">
	import { Button } from '$lib/components/ui/button';
	import { Typography } from '$lib/components/ui/typography';
	import SEO from '$lib/components/seo/index.svelte';
	import website from '$lib/config/website';

	const { siteTitle, siteDescription } = website;

	const ldJson = {
		'@context': 'https://schema.org',
		'@type': 'WebSite',
		name: siteTitle,
		url: website.siteUrl,
		description: siteDescription
	};
	const jsonldScript = `<script type="application/ld+json">${
		JSON.stringify(ldJson) + '<'
	}/script>`;
</script>

<SEO
	title="Home"
	metadescription={siteDescription}
	slug=""
	ogImage={{
		url: website.siteImage,
		alt: "Reletino - AI-Powered Lead Generation"
	}}
	ogSquareImage={{
		url: website.siteImageSquare,
		alt: "Reletino - AI-Powered Lead Generation"
	}}
/>

<main class="bg-background z-10 -mt-32">
	<div class="relative">
		<div
			class="from-tertiary via-secondary to-primary absolute inset-2 bottom-0 rounded-3xl bg-[linear-gradient(115deg,var(--tw-gradient-stops))] from-[28%] ring-1 ring-inset ring-black/5 sm:bg-[linear-gradient(145deg,var(--tw-gradient-stops))]"
		></div>
		<div
			class="text-primary-foreground relative flex flex-col place-items-start rounded-3xl px-12 py-44 text-start lg:px-24 lg:pb-12"
		>
			<div class="">
				<Typography
					class="text-balance text-start text-6xl/[0.9] font-medium tracking-tight sm:text-8xl/[0.8] md:text-9xl/[0.8]"
				>
					Close every deal.
				</Typography>
				<Typography
					variant="title-md"
					class="max-w-xl pt-8 text-start text-xl/7 font-medium sm:text-2xl/8"
				>
					Reletino helps SaaS owners sell more by <br />
					revealing leads from Reddit, through an AI Agent.
				</Typography>
			</div>
			<div class="mt-12 flex flex-col gap-6 gap-x-6 gap-y-4 sm:flex-row">
				<Button
					href="/onboarding"
					class="bg-background text-foreground hover:bg-background/80 w-full rounded-3xl"
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
	</div>

	<div
		class="from-primary via-secondary to-tertiary mx-auto my-12 max-w-5xl rounded-3xl bg-[linear-gradient(115deg,var(--tw-gradient-stops))] from-[28%] p-1.5 sm:bg-[linear-gradient(145deg,var(--tw-gradient-stops))]"
	>
		<div class="" style="position: relative; padding-bottom: 56.25%; height: 0;">
			<iframe
				class="rounded-3xl"
				src="https://www.loom.com/embed/61475d8b2c264c309348aa88b52e7f9e?sid=f6efc182-732e-475c-91d5-64aeafeac636"
				frameborder="0"
				webkitallowfullscreen
				mozallowfullscreen
				allowfullscreen
				style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;"
			></iframe>
		</div>
	</div>
</main>
