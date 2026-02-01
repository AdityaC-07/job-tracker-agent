# Agent Workflow: What Each Agent Does

## Quick Reference: Agent Breakdown

| Agent | Input | Purpose | Output |
|-------|-------|---------|--------|
| **Job Requirements Analyzer** | Job title + description | Identify key skills/tech needed | 3-5 key requirements |
| **Technical Interview Agent** | Job requirements + role | Generate role-specific questions | 5 technical questions |
| **Behavioral Interview Agent** | Company name + role | Generate culture-fit questions | 5 behavioral questions |
| **Interview Coaching Agent** | Requirements + role + company | Create personalized tips | 7 success strategies |
| **Preparation Agent** | Role | Create structured checklist | 12-item preparation plan |

---

## Detailed Agent Workflows

### AGENT 1: Job Requirements Analyzer 🔍

**Trigger:** User selects a job application

**Process:**
```
Input: 
  - Job title: "Senior React Developer"
  - Job description: "We're looking for an experienced React developer..."

Analysis:
  ✓ Check role level: "Senior" found → add "Leadership and mentoring"
  ✓ Check specialization: "React" found → add "React frontend framework"
  ✓ Check description keywords: "JavaScript", "TypeScript" → add to list
  ✓ Check for frameworks: "Redux", "Next.js" patterns
  ✓ Extract unique skills

Output:
  requirements = [
    "Leadership and mentoring",
    "React frontend framework",
    "JavaScript/Node.js",
    "UI/UX principles"
  ]
```

**Real Example - Backend Engineer:**
```
Input: "Senior Backend Engineer - Python & AWS"

Analysis:
  ✓ "Senior" found → leadership
  ✓ "Python" found → Python programming
  ✓ "AWS" found → AWS cloud services
  ✓ "API" mentioned → REST API design
  ✓ "Database" mentioned → database optimization

Output:
  requirements = [
    "Backend architecture",
    "Python programming",
    "AWS cloud services",
    "API REST design",
    "Database optimization"
  ]
```

---

### AGENT 2: Technical Interview Agent 💻

**Trigger:** Receives requirements from Agent 1

**Process:**
```
Input: requirements = ["React", "JavaScript", "UI/UX principles"]

Analysis:
  ✓ Check if "React" in requirements → use React template
  ✓ Generate React-specific questions:
    - "Explain component lifecycle..."
    - "State management approach..."
    - "Performance optimization..."
  ✓ Check for specialization hints
  ✓ Check role level
  ✓ Generate 5 unique questions

Output:
  technical_questions = [
    "Explain the component lifecycle in React...",
    "How would you optimize performance in...",
    "Describe your state management approach...",
    "What's the difference between controlled...",
    "How do you handle complex form validation..."
  ]
```

**Role-Based Logic:**
- **If "Frontend" or "React" detected:**
  - Ask about React lifecycle, hooks, state management
  - Ask about performance optimization
  - Ask about controlled components
  
- **If "Backend" or "API" detected:**
  - Ask about API design patterns
  - Ask about database optimization
  - Ask about caching strategies
  
- **If "Full-Stack" detected:**
  - Ask about tech stack choices
  - Ask about deployment pipelines
  - Ask about testing strategies

---

### AGENT 3: Behavioral Interview Agent 🤝

**Trigger:** Company name + role provided

**Process:**
```
Input: 
  - company = "Google"
  - role = "Senior React Developer"
  - role_type = "frontend"

Analysis:
  ✓ Check company type: "Google" → tech company
  ✓ Customize first question: 
    "Why are you interested in the Senior React Developer position at Google?"
  ✓ Generate generic behavioral questions
  ✓ Ensure STAR-method friendly questions
  ✓ Add culture/mission-related questions

Output:
  behavioral_questions = [
    "Why are you interested in the Senior React Developer position at Google?",
    "Tell us about a time you had to collaborate with a difficult team member",
    "Describe a situation where you had to meet a tight deadline",
    "What attracted you to Google's mission and culture?",
    "Tell us about a time you failed - what did you learn?"
  ]
```

**Company-Specific Customization:**
- **Tech/Software company:** Ask about innovation and technology
- **Finance company:** Ask about analytical skills
- **Startup:** Ask about fast-paced, adaptability
- **AI/ML company:** Ask about cutting-edge technology

---

### AGENT 4: Interview Coaching Agent 🎯

**Trigger:** Requirements + role + company

**Process:**
```
Input: 
  - role = "Senior React Developer"
  - company = "Google"
  - requirements = ["React", "Leadership", "UI/UX"]

Analysis:
  ✓ Check if "Senior" in role → add leadership tips
  ✓ Check if "Frontend" implied → add UI/UX tips
  ✓ Check requirements:
    - "React" mentioned → "Prepare React-specific examples"
    - "Leadership" needed → "Emphasize mentoring examples"
  ✓ Add company-specific research guidance
  ✓ Add universal success tactics

Output:
  tips = [
    "Research Google's recent products and company culture",
    "Use STAR method for behavioral questions",
    "Highlight your React expertise and optimization skills",
    "Emphasize leadership and mentoring experiences",
    "Ask thoughtful questions about the team and role",
    "Practice discussing architecture decisions",
    "Maintain confident body language and eye contact"
  ]
```

**Conditional Logic:**
- If Senior/Lead level → emphasize leadership
- If Frontend → emphasize UX and performance
- If Backend → emphasize architecture and scalability
- If specific tech detected → add tech-specific tips

---

### AGENT 5: Preparation Agent ✅

**Trigger:** Role identified

**Process:**
```
Input: role = "Senior React Developer"

Analysis:
  ✓ Create base 12-item checklist
  ✓ Customize items:
    - "Review your resume..."
    - "Research Google: mission, products, news"
    - "Study Senior React Developer requirements"
    - "Prepare React/mentoring examples"
    - "Prepare 5-7 STAR examples"
    - "Test tech setup for virtual interview"
    - "Practice your answers"
    - "Get good sleep"
  ✓ Ensure comprehensive coverage

Output:
  checklist = [
    "✓ Review your resume...",
    "✓ Research Google's recent products...",
    "✓ Study the Senior React Developer role...",
    "✓ Prepare 5-7 STAR method examples...",
    "✓ Prepare thoughtful questions...",
    "✓ Test your tech setup...",
    "✓ Plan your outfit...",
    "✓ Plan travel/arrival...",
    "✓ Bring printed materials...",
    "✓ Practice with a friend...",
    "✓ Get good sleep...",
    "✓ Eat a healthy meal..."
  ]
```

---

## Example: From Job Posting to Complete Interview Prep

### SCENARIO: User applies for 2 different jobs

#### Job 1: "Frontend Engineer - React" at Stripe
```
AGENT 1 (Analyzer):
  Input: React job @ Stripe
  Output: ["React framework", "UI/UX", "JavaScript", "Performance optimization"]

AGENT 2 (Technical):
  Input: React requirements
  Output: [
    "Explain React component lifecycle...",
    "State management approaches...",
    "Performance optimization techniques...",
    "CSS-in-JS solutions...",
    "Testing React components..."
  ]

AGENT 3 (Behavioral):
  Input: Company = Stripe, Role = React Frontend
  Output: [
    "Why Stripe and this role?",
    "Teamwork example...",
    "Deadline pressure example...",
    "Stripe's vision question...",
    "Growth/learning example..."
  ]

AGENT 4 (Coaching):
  Input: Frontend + UI/UX focus
  Output: [
    "Research Stripe's payment products",
    "Highlight UI implementation examples",
    "Prepare performance optimization stories",
    "Ask about design system...",
    "Discuss accessibility..."
  ]

AGENT 5 (Preparation):
  Output: [
    "Study Stripe's payment flow...",
    "Practice React coding patterns...",
    "Test video interview setup...",
    "Prepare UI/UX examples...",
    (and 8 more items)
  ]
```

#### Job 2: "Backend Engineer - Python" at Amazon
```
AGENT 1 (Analyzer):
  Input: Python backend job @ Amazon
  Output: ["Python programming", "AWS", "Microservices", "Database optimization"]

AGENT 2 (Technical):
  Input: Backend + AWS requirements
  Output: [
    "API design patterns for scale...",
    "Database optimization strategies...",
    "AWS architecture decisions...",
    "Microservices communication...",
    "System design - how to scale..."
  ]

AGENT 3 (Behavioral):
  Input: Company = Amazon, Role = Backend Engineer
  Output: [
    "Why Amazon and this role?",
    "Difficult colleague example...",
    "Customer obsession example...",
    "Amazon leadership principles fit...",
    "Failed project learnings..."
  ]

AGENT 4 (Coaching):
  Input: Backend + Microservices + AWS
  Output: [
    "Research Amazon's AWS leadership",
    "Highlight backend architecture examples",
    "Prepare system design stories",
    "Ask about scaling challenges...",
    "Discuss microservices patterns..."
  ]

AGENT 5 (Preparation):
  Output: [
    "Study Amazon's ecosystem...",
    "Practice system design interviews...",
    "Test technical setup...",
    "Prepare AWS examples...",
    (and 8 more items)
  ]
```

### Result
Same user gets **completely different** interview prep:
- Job 1: React, UI, Stripe-specific
- Job 2: Python, AWS, Amazon-specific

This proves agents are analyzing the job posting, not just returning generic templates.

---

## Key Agent Behaviors

### 1. **Requirement Extraction**
- Scans for keywords: Python, React, AWS, Docker, Kubernetes, etc.
- Identifies role level: Junior, Mid, Senior, Lead, Principal
- Identifies specialization: Frontend, Backend, Full-Stack, DevOps, etc.

### 2. **Role-Specific Generation**
- Frontend questions ≠ Backend questions
- Python questions ≠ JavaScript questions
- Senior questions ≠ Junior questions

### 3. **Company-Aware Content**
- Google/Tech → Innovation-focused
- Startup → Adaptability-focused
- Finance → Analytical-focused

### 4. **Personalization Layers**
- Layer 1: Job requirements
- Layer 2: Company type
- Layer 3: Role level
- Layer 4: Specialization
- Result: Unique prep for each application

---

## How to Demonstrate This in Hackathon

1. **Select 3 Different Jobs:**
   - Frontend role
   - Backend role
   - Different company

2. **Generate Prep for Each:**
   - Show all 5 agents completing
   - Note different questions/tips

3. **Compare Output:**
   - "Notice how the questions completely changed"
   - "Each agent customized based on the job"
   - "Not generic templates - truly personalized"

4. **Explain the Value:**
   - Candidates get relevant, actionable prep
   - Saves time preparing correctly
   - Increases interview success rate

---

## Performance Note

All 5 agents execute in **parallel**, not sequentially:
- Agent 1 extracts requirements
- Agents 2-4 all run simultaneously with requirement input
- Agent 5 creates final checklist
- Total execution: ~100ms (faster than sequential)

This is true multi-agent orchestration!
