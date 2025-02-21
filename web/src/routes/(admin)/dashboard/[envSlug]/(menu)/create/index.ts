export type ProjectSetup = {
    objective: string;
    selectedSubreddits: string[];
    filteringPrompt: string;
    projectName: string;
    saasUrl: string;
    saasDescription: string;
    mode: 'advanced' | 'simple';
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
    { label: "Find Influencers", value: "find_influencers" },
    { label: "Find Investors", value: "find_investors" },
    { label: "Find Partners", value: "find_partners" },
]; 