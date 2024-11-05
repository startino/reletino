<script lang="ts">
	import * as Card from '$lib/components/ui/card';
	import { Button } from '$lib/components/ui/button';
	import { ChevronLeft, ChevronRight } from 'lucide-svelte';
	import { Typography } from '$lib/components/ui/typography';
	import * as Select from '$lib/components/ui/select';

	let currentStep: 0 | 1 | 2 | 3 = $state(0);
	const stepToTitle = {
		0: 'Choose a category',
		1: 'Give your project a name',
		2: 'Enter your website URL',
		3: 'Provide additional data',
	};

	const next = () => {
		if (currentStep === 3) return;
		currentStep++;
	};

	const prev = () => {
		if (currentStep === 0) return;
		currentStep--;
	};
</script>

<div class=" mx-auto max-w-2xl">
	<Typography as="h1" variant="headline-sm" class="mb-6">Create a project</Typography>
	<Card.Root>
		<Card.Header>
			<Card.Title>{stepToTitle[currentStep]}</Card.Title>
		</Card.Header>

		<Card.Content>
			<p>Content</p>
		</Card.Content>
		<Card.Footer class="flex gap-2">
			<Button onclick={prev} size="icon" disabled={currentStep === 0} variant="ghost">
				<ChevronLeft />
			</Button>
			<Button onclick={next} size="icon" disabled={currentStep === 3} variant="ghost">
				<ChevronRight />
			</Button>
		</Card.Footer>
	</Card.Root>
</div>
