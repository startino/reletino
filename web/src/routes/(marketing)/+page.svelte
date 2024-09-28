<script lang="ts">
  import { WebsiteName, WebsiteBaseUrl, WebsiteDescription } from "$lib/config"
  import { buttonVariants } from "$lib/components/ui/button"
  import * as Card from "$lib/components/ui/card"

  const ldJson = {
    "@context": "https://schema.org",
    "@type": "WebSite",
    name: WebsiteName,
    url: WebsiteBaseUrl,
  }
  const jsonldScript = `<script type="application/ld+json">${
    JSON.stringify(ldJson) + "<"
  }/script>`
</script>

<svelte:head>
  <title>{WebsiteName}</title>
  <meta name="description" content={WebsiteDescription} />
  <!-- eslint-disable-next-line svelte/no-at-html-tags -->
  {@html jsonldScript}
</svelte:head>

<div class="max-w-7xl mx-auto min-h-[60vh] my-auto place-items-center grid">
  <div class="mx-auto w-fit text-center">
    <div class="max-w-xl">
      <div
        class="text-xl md:text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-primary to-accent mb-4 md:mb-8"
      >
        reletino
      </div>

      <div
        class="text-4xl md:text-6xl font-bold px-2"
        style="line-height: 1.2;"
      >
      Get relevant posts
        <span
          class="underline decoration-secondary decoration-4 md:decoration-[6px]"
          >
          with plain English</span
        >
        
        <span class="underline decoration-pink-900 decoration-4 md:decoration-[6px]">not keywords</span>
      </div>
      <div class="mt-6 md:mt-10 text-sm md:text-lg">
        <p>
          Reletino is an AI agent with a powerful feedback loop to understand your <br />
          nuanced definition of which Reddit posts are actually useful to you. <br /> <br/>
          If you have a product or service to offer, Reletino is for you.
        </p>
        
      </div>
      <div class="mt-6 md:mt-2">
        <a
          href="/onboarding"
          class="{buttonVariants({ variant: 'default' })} mt-4 md:mt-8"
        >
          Get Started
        </a>
      </div>
    </div>
  </div>
</div>
