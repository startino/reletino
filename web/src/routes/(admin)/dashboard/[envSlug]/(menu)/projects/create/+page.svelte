<script lang="ts">
	import * as Card from '$lib/components/ui/card';
	import { Button } from '$lib/components/ui/button';
	import { ChevronLeft, ChevronRight } from 'lucide-svelte';
	import { Typography } from '$lib/components/ui/typography';
	import { Input } from '$lib/components/ui/input';
	import { Label } from '$lib/components/ui/label';
	import { superForm } from 'sveltekit-superforms/client';
	import { Badge } from '$lib/components/ui/badge';
	import { X, Plus } from 'lucide-svelte';
	import { zod } from 'sveltekit-superforms/adapters';
	import { projectCreationSchema } from '$lib/schemas.js';

	let currentStep: 1 | 2 | 3 | 4 | 5 = $state(1);
	let selectedCategory = $state('');
	let projectName = $state('');
	let websiteUrl = $state('');

	const categories = [
		{ value: 'find-leads', label: 'Find Leads' },
		{ value: 'find-competition', label: 'Find Competition' },
	];

	const stepToTitle = {
		1: 'Choose a category',
		2: 'Give your project a name',
		3: 'Enter your website URL',
		4: 'Provide additional data',
		5: 'Preview and confirm',
	};

	const next = async () => {
		if (currentStep === 5) return;
		if (currentStep === 3 && websiteUrl) {
			const result = await validate('websiteUrl');
			if (result && result[0]) {
				$errors.websiteUrl = result;
				console.log($errors.websiteUrl);
				return;
			}
		}
		currentStep++;
	};

	const prev = () => {
		if (currentStep === 1) return;
		currentStep--;
	};

	let { data } = $props();

	const { form, enhance, errors, validate } = superForm(data.form, {
		resetForm: false,
		taintedMessage: null,
		dataType: 'json',
		validators: zod(projectCreationSchema),
	});

	let irrelevantPostExample = $state('');
	let coreFeature = $state('');

	$effect(() => {
		$form.category = selectedCategory as 'find-leads' | 'find-competition';
		$form.projectName = projectName;
		$form.websiteUrl = websiteUrl === '' ? null : websiteUrl;

		if (selectedCategory === 'find-leads') {
			$form.context = {
				category: selectedCategory,
				product_name: '',
				icp: '',
				irrelevant_post_examples: [],
			};
		} else if (selectedCategory === 'find-competition') {
			$form.context = {
				category: selectedCategory,
				name: '',
				core_features: [],
			};
		}
	});
</script>

<div class="mx-auto max-w-2xl">
	<Typography as="h1" variant="headline-sm" class="mb-6">Create a project</Typography>
	<Card.Root>
		<Card.Header>
			<Card.Title>{stepToTitle[currentStep]}</Card.Title>
			<Card.Description>Step {currentStep} of 5</Card.Description>
		</Card.Header>

		<Card.Content>
			{#if currentStep === 1}
				<div class="space-y-2">
					<Label for="category">Category</Label>
					<select
						id="category"
						class="border-input bg-background w-full rounded-md border px-3 py-2"
						bind:value={selectedCategory}
					>
						<option value="">Select a category</option>
						{#each categories as category}
							<option value={category.value}>{category.label}</option>
						{/each}
					</select>
				</div>
			{:else if currentStep === 2}
				<div class="space-y-2">
					<Label for="project-name">Project name</Label>
					<Input
						id="project-name"
						placeholder="Enter project name"
						bind:value={projectName}
					/>
				</div>
			{:else if currentStep === 3}
				<div class="space-y-2">
					<Label for="website-url">Website URL (optional)</Label>
					<Input
						id="website-url"
						type="url"
						placeholder="https://example.com"
						bind:value={websiteUrl}
						class={$errors.websiteUrl ? 'border-destructive' : ''}
					/>

					{#if $errors.websiteUrl}
						<p class="text-destructive text-sm">{$errors.websiteUrl}</p>
					{/if}
				</div>
			{:else if currentStep === 4}
				<form method="POST" use:enhance>
					<input type="hidden" name="category" value={selectedCategory} />

					{#if $form.context.category === 'find-leads'}
						<div class="space-y-4">
							<div class="space-y-2">
								<Label for="product-name">Product Name</Label>
								<Input
									id="product-name"
									name="data.product_name"
									bind:value={$form.context.product_name}
								/>
							</div>

							<div class="space-y-2">
								<Label for="icp">ICP</Label>
								<Input id="icp" name="data.icp" bind:value={$form.context.icp} />
							</div>

							<div class="space-y-2">
								<Label>Irrelevant Post Examples</Label>
								<div class="flex gap-2">
									<Input
										bind:value={irrelevantPostExample}
										placeholder="Add example"
										onkeydown={(e) => {
											if (e.key === 'Enter') {
												e.preventDefault();
												if (irrelevantPostExample) {
													$form.context.category === 'find-leads' &&
														($form.context.irrelevant_post_examples = [
															...$form.context
																.irrelevant_post_examples,
															irrelevantPostExample,
														]);
													irrelevantPostExample = '';
												}
											}
										}}
									/>
									<Button
										type="button"
										variant="outline"
										onclick={() => {
											if (irrelevantPostExample) {
												$form.context.category === 'find-leads' &&
													($form.context.irrelevant_post_examples = [
														...$form.context.irrelevant_post_examples,
														irrelevantPostExample,
													]);
												irrelevantPostExample = '';
											}
										}}
									>
										<Plus />
									</Button>
								</div>
								{#if $form.context.irrelevant_post_examples.length > 0}
									<div class="flex flex-wrap gap-2">
										{#each $form.context.irrelevant_post_examples as example}
											<Badge variant="outline" class="gap-1.5">
												{example}
												<button
													type="button"
													class="hover:text-destructive"
													onclick={() => {
														$form.context.category === 'find-leads' &&
															($form.context.irrelevant_post_examples =
																$form.context.irrelevant_post_examples.filter(
																	(r) => r !== example
																));
													}}
												>
													<X class="h-3 w-3" />
												</button>
											</Badge>
										{/each}
									</div>
								{/if}
							</div>
						</div>
					{:else if $form.context.category === 'find-competition'}
						<div class="space-y-4">
							<div class="space-y-2">
								<Label for="name">Name</Label>
								<Input id="name" name="data.name" bind:value={$form.context.name} />
							</div>

							<div class="space-y-2">
								<Label>Core Features</Label>
								<div class="flex gap-2">
									<Input
										bind:value={coreFeature}
										placeholder="Add feature"
										onkeydown={(e) => {
											if (e.key === 'Enter') {
												e.preventDefault();
												if (coreFeature) {
													$form.context.category === 'find-competition' &&
														($form.context.core_features = [
															...$form.context.core_features,
															coreFeature,
														]);
													coreFeature = '';
												}
											}
										}}
									/>
									<Button
										type="button"
										variant="icon"
										onclick={() => {
											if (coreFeature) {
												$form.context.category === 'find-competition' &&
													($form.context.core_features = [
														...$form.context.core_features,
														coreFeature,
													]);
												coreFeature = '';
											}
										}}
									>
										<Plus />
									</Button>
								</div>
								{#if $form.context.core_features.length > 0}
									<div class="flex flex-wrap gap-2">
										{#each $form.context.core_features as feature}
											<Badge variant="outline" class="gap-1.5">
												{feature}
												<button
													type="button"
													class="text-muted-foreground hover:text-foreground"
													onclick={() => {
														$form.context.category ===
															'find-competition' &&
															($form.context.core_features =
																$form.context.core_features.filter(
																	(r) => r !== feature
																));
													}}
												>
													<X class="h-3 w-3" />
												</button>
											</Badge>
										{/each}
									</div>
								{/if}
							</div>
						</div>
					{/if}
				</form>
			{:else}
				<div class="space-y-6">
					<div class="space-y-2">
						<Typography as="h2" variant="body-md" class="font-bold">
							Project Details
						</Typography>
						<div class="grid grid-cols-[auto_1fr] gap-2 text-sm">
							<div class="font-medium">Category:</div>
							<div>{categories.find((c) => c.value === selectedCategory)?.label}</div>

							<div class="font-medium">Project Name:</div>
							<div>{projectName}</div>

							{#if websiteUrl}
								<div class="font-medium">Website URL:</div>
								<div>{websiteUrl}</div>
							{/if}
						</div>
					</div>

					{#if $form.context.category === 'find-leads'}
						<div class="space-y-2">
							<Typography as="h2" variant="body-md" class="font-bold">
								Lead Finding Configuration
							</Typography>
							<div class="grid grid-cols-[auto_1fr] gap-2 text-sm">
								<div class="font-medium">Product Name:</div>
								<div>{$form.context.product_name}</div>

								<div class="font-medium">ICP:</div>
								<div>{$form.context.icp}</div>
							</div>

							{#if $form.context.irrelevant_post_examples.length > 0}
								<div class="space-y-2">
									<div class="text-sm font-medium">Irrelevant Post Examples:</div>
									<div class="flex flex-wrap gap-2">
										{#each $form.context.irrelevant_post_examples as example}
											<Badge variant="outline">{example}</Badge>
										{/each}
									</div>
								</div>
							{/if}
						</div>
					{:else if $form.category === 'find-competition'}
						<div class="space-y-2">
							<Typography as="h2" variant="body-md" class="font-bold">
								Competition Finding Configuration
							</Typography>
							<div class="grid grid-cols-[auto_1fr] gap-2 text-sm">
								<div class="font-medium">Name:</div>
								<div>{$form.context.name}</div>
							</div>

							{#if $form.context.core_features.length > 0}
								<div class="space-y-2">
									<div class="text-sm font-medium">Core Features:</div>
									<div class="flex flex-wrap gap-2">
										{#each $form.context.core_features as feature}
											<Badge variant="outline">{feature}</Badge>
										{/each}
									</div>
								</div>
							{/if}
						</div>
					{/if}

					<form method="POST" use:enhance>
						<input type="hidden" name="category" bind:value={$form.category} />
						<input type="hidden" name="projectName" bind:value={$form.projectName} />
						<input type="hidden" name="websiteUrl" bind:value={$form.websiteUrl} />

						{#if $form.context.category === 'find-leads'}
							<input
								type="hidden"
								name="data.product_name"
								value={$form.context.product_name}
							/>
							<input type="hidden" name="data.icp" value={$form.context.icp} />
							{#each $form.context.irrelevant_post_examples as example, index}
								<input
									type="hidden"
									name={`data.irrelevant_post_examples[${index}]`}
									value={example}
								/>
							{/each}
						{:else if $form.context.category === 'find-competition'}
							<input type="hidden" name="data.name" value={$form.context.name} />
							{#each $form.context.core_features as feature, index}
								<input
									type="hidden"
									name={`data.core_features[${index}]`}
									value={feature}
								/>
							{/each}
						{/if}

						<Button type="submit" class="w-full">Create Project</Button>

						{#if $errors._errors}
							<p class="text-destructive">{$errors._errors[0]}</p>
						{/if}
					</form>
				</div>
			{/if}
		</Card.Content>

		<Card.Footer class="">
			<Button onclick={prev} size="sm" disabled={currentStep === 1} variant="ghost">
				<ChevronLeft /> Previous
			</Button>
			<Button
				onclick={next}
				size="sm"
				disabled={currentStep === 5 ||
					(currentStep === 1 && !selectedCategory) ||
					(currentStep === 2 && !projectName) ||
					(currentStep === 3 && $errors.websiteUrl) ||
					(currentStep === 4 &&
						(($form.context.category === 'find-leads' &&
							(!$form.context.product_name || !$form.context.icp)) ||
							($form.context.category === 'find-competition' &&
								!$form.context.name)))}
				variant="ghost"
			>
				Next <ChevronRight />
			</Button>
		</Card.Footer>
	</Card.Root>
</div>
