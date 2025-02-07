# Reletino Platform Documentation

## Overview
Reletino is a Reddit Sales platform that helps SaaS companies find and engage with potential leads on Reddit through AI-powered automation. The platform uses advanced AI to identify relevant posts, analyze them for sales opportunities, and engage with prospects in a personalized way.

## Core Features

### 1. Project Management
- **Project Creation**
  - Users can create projects
  - Project setup includes:
    - Website URL integration
    - Target subreddits configuration
    - Prompt for Filtering Agent
    - Prompt for Comment and DM Generation Agent

### 2. AI-Powered Lead Generation
- **Automated Reddit Monitoring**
  - Real-time monitoring of specified subreddits
  - Smart filtering of relevant posts based on plain English
  - Automatic lead qualification
  
- **Intelligent Response Generation**
  - AI-generated responses to relevant posts
  - Customizable DM style and tone
  - Context-aware messaging based on post content
  - Feedback-based response improvement

### 3. Dashboard & Analytics
- **Project Overview**
  - Active project status monitoring
  - Real-time submission tracking
  - Filter options for:
    - Read/unread submissions
    - Relevant/irrelevant content
  - Project performance metrics


## User Flows

### 1. Onboarding Flow
1. Sign Up/Sign In
2. Create Profile
   - Enter full name
   - Enter company name
3. Project Setup

### 2. Project Creation Flow
1. Select project objective (Lead Finding/Competition Research)
2. Enter SaaS URL or description
   - Website URL / Product description
3. AI Generation
   - Filtering Agent Prompt
   - Recommend subreddits
4. Review and confirm settings
5. Activate project

### 3. Lead Management Flow
1. View incoming submissions in dashboard
2. Filter and sort submissions
3. Review potential leads
4. Generate AI responses
5. Track engagement
6. Manage follow-ups

## Technical Capabilities

### AI Features
- LLM integration for comment/DM generation
- Submission relevance evaluation for filtering
- All AI Systems have a human in the loop feedback system to learn over time


## Data Structures

### Example Submission
```json
{
  "id": "123",
  "profile_id": "456", 
  "project_id": "789",
  "title": "Looking for recommendations for a project management tool",
  "selftext": "Hi everyone, I'm looking for a project management tool for my small team. We need something simple but powerful that can handle task tracking and collaboration. Any suggestions?",
  "url": "https://reddit.com/r/saas/comments/abc123",
  "author": "user123",
  "subreddit": "saas",
  "submission_created_utc": "2024-01-01T10:00:00Z",
  "is_relevant": true,
  "reasoning": "This user is actively looking for a project management solution, which makes them a potential lead. They've provided clear requirements and seem to be in a decision-making position.",
  "done": false,
  "approved_evaluation": null,
  "approved_comment": null,
  "approved_dm": null,
  "profile_insights": "Active in r/saas, r/startups\nFrequently discusses team collaboration and productivity tools\nLikely a startup founder or team lead based on post history"
}
```

### Example Project
```json
{
  "id": "789",
  "profile_id": "456",
  "title": "Project Management Tool Leads",
  "prompt": "<html content for filtering criteria>",
  "comment_style_prompt": "<html content for comment styling>",
  "dm_style_prompt": "<html content for DM styling>",
  "subreddits": ["saas", "startups", "productivity"],
  "running": true
}
```

### Example Analysed Profile
```json
{
  "username": "user123",
  "profile_insights": {
    "basic_information": {
      "username": "user123",
      "karma": {
        "total": 1500,
        "comment": 800,
        "post": 700
      },
      "account_creation": "2023-01-01",
      "identified_demographics": {
        "age_range": "25-35",
        "gender": "male",
        "location": "New York, USA",
        "timezone": "EST"
      }
    },
    "professional_background": {
      "occupation": "Startup Founder",
      "industry": "Technology",
      "company_stage": "Early Stage",
      "skills": ["Product Management", "Team Leadership"],
      "previous_experience": ["Product Manager at Tech Company"]
    },
    "interests": {
      "active_subreddits": [
        "saas",
        "startups",
        "productivity"
      ],
      "topics": [
        "SaaS Development",
        "Team Collaboration",
        "Productivity Tools"
      ],
      "hobbies": [
        "Tech Meetups",
        "Entrepreneurship"
      ]
    },
    "behavioral_patterns": {
      "posting_frequency": "Regular",
      "engagement_style": "Helpful and detailed",
      "communication_tone": "Professional",
      "preferred_topics": [
        "Business Strategy",
        "Tool Recommendations",
        "Startup Advice"
      ]
    },
    "business_relevance": {
      "decision_maker": true,
      "buying_stage": "Research",
      "pain_points": [
        "Seeking efficient project management solutions",
        "Need for automation tools"
      ],
      "potential_fit": "High"
    },
    "raw_analysis": "<html>Original HTML format analysis from AI</html>"
  }
}
```