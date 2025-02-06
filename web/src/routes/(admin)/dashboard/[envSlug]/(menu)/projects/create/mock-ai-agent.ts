type GeneratedContent = {
    subreddits: string[];
    filteringPrompt: string;
};

const MOCK_RESPONSES: Record<string, GeneratedContent> = {
    find_leads: {
        subreddits: ['startups', 'entrepreneur', 'smallbusiness', 'SaaS'],
        filteringPrompt: `Look for posts and comments that indicate:
- Users expressing pain points or challenges in their business
- Questions about solutions similar to our offering
- Discussions about pricing or costs related to our industry
- Requests for recommendations in our product category`
    },
    find_competitors: {
        subreddits: ['technology', 'business', 'marketing', 'ProductManagement'],
        filteringPrompt: `Analyze posts and comments for:
- Mentions of competing products or services
- Feature comparisons between different solutions
- User reviews and feedback about competitors
- Market trends and emerging players in the space`
    },
    find_inspiration: {
        subreddits: ['UI_Design', 'webdev', 'Design', 'UserExperience'],
        filteringPrompt: `Search for content related to:
- Innovative UI/UX solutions
- User feedback on design and functionality
- Feature requests and wishlists
- Discussions about user experience improvements`
    }
};

export async function generateSubredditsAndPrompt(objective: string): Promise<GeneratedContent> {
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 1500));
    
    return MOCK_RESPONSES[objective] || {
        subreddits: ['all'],
        filteringPrompt: 'Look for relevant discussions and user needs in this space.'
    };
} 