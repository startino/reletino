<script lang="ts">
    import { Typography } from '$lib/components/ui/typography';
    import { Construction } from 'lucide-svelte';
</script>

<div class="flex flex-col items-center justify-center min-h-[80vh] gap-6 text-center px-4">
    <Construction class="w-24 h-24 text-primary animate-bounce" />
    
    <div class="space-y-2">
        <Typography variant="h2" class="text-primary">Lead Manager</Typography>
        <Typography variant="h4">Coming Soon</Typography>
    </div>
    
    <Typography variant="body" class="max-w-md text-muted-foreground">
        We're working hard to bring you a powerful lead management system. Stay tuned for updates!
    </Typography>
</div> 