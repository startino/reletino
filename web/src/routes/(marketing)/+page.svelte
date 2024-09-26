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

  const features = [
  ]
</script>

<svelte:head>
  <title>{WebsiteName}</title>
  <meta name="description" content={WebsiteDescription} />
  <!-- eslint-disable-next-line svelte/no-at-html-tags -->
  {@html jsonldScript}
</svelte:head>

<div class="hero min-h-[60vh]">
  <div class="hero-content text-center py-12">
    <div class="max-w-xl">
      <div
        class="text-xl md:text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-primary to-accent mb-4 md:mb-8"
      >
        SaaS Starter Demo
      </div>

      <div
        class="text-4xl md:text-6xl font-bold px-2"
        style="line-height: 1.2;"
      >
        The
        <span
          class="underline decoration-secondary decoration-4 md:decoration-[6px]"
          >open source</span
        >,
        <span
          class="underline decoration-secondary decoration-4 md:decoration-[6px]"
          >fast</span
        >, and
        <span
          class="underline decoration-secondary decoration-4 md:decoration-[6px]"
          >free to host</span
        >
        <span> SaaS template</span>
      </div>
      <div class="mt-6 md:mt-10 text-sm md:text-lg">
        Built with <a
          href="https://kit.svelte.dev"
          class="link font-bold"
          target="_blank">SvelteKit</a
        >,
        <a
          href="https://supabase.com"
          class="underline font-bold"
          target="_blank">Supabase</a
        >,
        <a href="https://stripe.com" class="underline font-bold" target="_blank"
          >Stripe</a
        >,
        <a
          href="https://tailwindcss.com"
          class="underline font-bold"
          target="_blank">Tailwind</a
        >,
        <a
          href="https://shadcn-svelte.com/"
          class="underline font-bold"
          target="_blank">Shadcn-Svelte</a
        >, and
        <a
          href="https://www.postgresql.org"
          class="link font-bold"
          target="_blank">Postgres</a
        >
      </div>
      <div class="mt-6 md:mt-2">
        <a href="https://github.com/CriticalMoments/CMSaasStarter">
          <button class={buttonVariants({ variant: "default" })}
            >★ us on Github</button
          >
        </a>
        <a
          href="https://github.com/CriticalMoments/CMSaasStarter/tree/main#saas-starter"
        >
          <button class={buttonVariants({ variant: "outline" })}
            >Read the Docs</button
          >
        </a>
      </div>
    </div>
  </div>
</div>

<div class="min-h-[60vh]">
  <div class="pt-20 pb-8 px-7">
    <div class="max-w-lg mx-auto text-center">
      <div
        class="text-3xl md:text-5xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-primary to-accent"
      >
        Explore the Features
      </div>
      <div class="mt-6 text-xl font-bold">
        And try them on this
        <span
          class="underline decoration-secondary decoration-[3px] md:decoration-[4px]"
        >
          fully functional demo
        </span>
      </div>
    </div>

    <div
      class="flex gap-6 mt-12 max-w-[1064px] mx-auto place-content-center flex-wrap"
    >
      {#each features as feature}
        <Card.Root
          class="flex items-center w-[270px] min-h-[300px] shadow-lg text-center"
        >
          <Card.Content class="grid justify-items-center">
            <div>
              <svg
                width="50px"
                height="50px"
                class="mb-2 mt-1"
                viewBox="0 0 24 24"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
              >
                <!-- eslint-disable-next-line svelte/no-at-html-tags -->
                {@html feature.svgContent}
              </svg>
            </div>
            <h2 class="text-xl font-bold">
              {feature.name}
            </h2>
            <p class="text-sm mb-3">
              {feature.description}
            </p>
            {#if feature.link}
              <a
                href={feature.link}
                class="{buttonVariants({
                  variant: 'outline',
                  size: 'sm',
                })} min-w-[100px]"
                target={feature.newPage ? "_blank" : ""}
              >
                {feature.linkText ? feature.linkText : "Try It"}
              </a>
            {/if}
          </Card.Content>
        </Card.Root>
      {/each}
    </div>
  </div>
</div>

<style>
  .hero {
    display: grid;
    width: 100%;
    place-items: center;
    background-size: cover;
    background-position: center;
  }

  .hero > * {
    grid-column-start: 1;
    grid-row-start: 1;
  }

  .hero-content {
    z-index: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    max-width: 80rem /* 1280px */;
    gap: 1rem /* 16px */;
    padding: 1rem /* 16px */;
  }
</style>
