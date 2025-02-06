export type ProjectSetup = {
    objective: string;
    selectedSubreddits: string[];
    filteringPrompt: string;
    saasUrl: string;
    saasDescription: string;
};

export type SetupStep = {
    title: string;
    description: string;
    isComplete: boolean;
};

export type Objective = {
    label: string;
    value: string;
};

export const OBJECTIVES: Objective[] = [
    { label: "Find Leads", value: "find_leads" },
    { label: "Find Competitors", value: "find_competitors" },
    { label: "Find Ideas", value: "find_ideas" },
    { label: "Find Content", value: "find_content" },
    { label: "Find Influencers", value: "find_influencers" },
    { label: "Find Investors", value: "find_investors" },
    { label: "Find Partners", value: "find_partners" },
    { label: "Find Suppliers", value: "find_suppliers" },
    { label: "Find Mentors", value: "find_mentors" },
    { label: "Find Mentees", value: "find_mentees" },
]; 