export interface AgentTemplate {
  id: string
  name: string
  description: string
  icon: string
  category: "core" | "specialist"
  boringTasks: string[]
  estimatedSavings: string
  tools: string[]
  outcomes: string[]
  complexity: "simple" | "medium" | "advanced"
}

export const agentTemplates: AgentTemplate[] = [
  {
    id: "crm",
    name: "CRM Agent",
    description: "Automates lead capture, follow-ups, customer segmentation, and sales pipeline updates",
    icon: "🎯",
    category: "specialist",
    boringTasks: [
      "Manual lead data entry",
      "Follow-up email scheduling",
      "Pipeline status updates",
      "Customer segmentation",
      "Lead scoring",
    ],
    estimatedSavings: "$2,400/month",
    tools: ["HubSpot API", "Salesforce API", "Gmail API", "Calendar API"],
    outcomes: ["Leads captured", "Follow-ups sent", "Deals moved", "Contacts updated"],
    complexity: "medium",
  },
  {
    id: "email_marketing",
    name: "Email Marketing Agent",
    description: "Handles email campaigns, drip sequences, abandoned cart reminders, and basic analytics",
    icon: "📧",
    category: "specialist",
    boringTasks: [
      "Email campaign creation",
      "Drip sequence setup",
      "Abandoned cart emails",
      "Newsletter scheduling",
      "A/B testing setup",
    ],
    estimatedSavings: "$1,800/month",
    tools: ["Mailchimp API", "SendGrid API", "Gmail API", "Analytics API"],
    outcomes: ["Emails sent", "Opens tracked", "Clicks measured", "Conversions recorded"],
    complexity: "simple",
  },
  {
    id: "invoice",
    name: "Invoice Agent",
    description: "Automates invoice creation, sending, payment reminders, and reconciliation",
    icon: "💰",
    category: "specialist",
    boringTasks: [
      "Invoice generation",
      "Payment reminder emails",
      "Receipt processing",
      "Expense categorization",
      "Financial reporting",
    ],
    estimatedSavings: "$3,200/month",
    tools: ["QuickBooks API", "Stripe API", "PayPal API", "Xero API"],
    outcomes: ["Invoices sent", "Payments processed", "Reminders sent", "Reports generated"],
    complexity: "medium",
  },
  {
    id: "scheduling",
    name: "Scheduling Agent",
    description: "Manages appointment bookings, reminders, and calendar sync",
    icon: "📅",
    category: "specialist",
    boringTasks: [
      "Appointment scheduling",
      "Calendar coordination",
      "Meeting reminders",
      "Availability checking",
      "Rescheduling requests",
    ],
    estimatedSavings: "$1,200/month",
    tools: ["Google Calendar API", "Calendly API", "Zoom API", "Teams API"],
    outcomes: ["Appointments booked", "Reminders sent", "Calendars synced", "No-shows reduced"],
    complexity: "simple",
  },
  {
    id: "social",
    name: "Social Media Agent",
    description: "Schedules and posts to social media, monitors engagement, and basic reporting",
    icon: "📱",
    category: "specialist",
    boringTasks: [
      "Social media posting",
      "Content scheduling",
      "Engagement monitoring",
      "Hashtag research",
      "Performance reporting",
    ],
    estimatedSavings: "$2,000/month",
    tools: ["Twitter API", "LinkedIn API", "Facebook API", "Instagram API"],
    outcomes: ["Posts published", "Engagement tracked", "Followers gained", "Reach measured"],
    complexity: "simple",
  },
  {
    id: "hr",
    name: "HR Agent",
    description: "Tracks time, manages leave requests, onboarding, and simple payroll notifications",
    icon: "👥",
    category: "specialist",
    boringTasks: [
      "Time tracking",
      "Leave request processing",
      "Employee onboarding",
      "Payroll notifications",
      "Performance reminders",
    ],
    estimatedSavings: "$2,800/month",
    tools: ["BambooHR API", "Slack API", "Google Sheets API", "Payroll API"],
    outcomes: ["Hours tracked", "Requests processed", "Employees onboarded", "Notifications sent"],
    complexity: "medium",
  },
  {
    id: "admin",
    name: "Admin Agent",
    description: "Fills out forms, collects routine data, generates simple reports, and manages document workflows",
    icon: "📋",
    category: "specialist",
    boringTasks: ["Form filling", "Data entry", "Report generation", "Document processing", "File organization"],
    estimatedSavings: "$1,600/month",
    tools: ["Google Forms API", "Airtable API", "Notion API", "PDF Generator"],
    outcomes: ["Forms completed", "Reports generated", "Documents processed", "Data organized"],
    complexity: "simple",
  },
  {
    id: "review",
    name: "Review Agent",
    description:
      "Monitors and responds to customer reviews, sends automated feedback requests, and compiles sentiment summaries",
    icon: "⭐",
    category: "specialist",
    boringTasks: [
      "Review monitoring",
      "Response drafting",
      "Feedback requests",
      "Sentiment analysis",
      "Rating tracking",
    ],
    estimatedSavings: "$1,400/month",
    tools: ["Google Reviews API", "Yelp API", "Trustpilot API", "Survey APIs"],
    outcomes: ["Reviews monitored", "Responses sent", "Feedback collected", "Sentiment tracked"],
    complexity: "simple",
  },
]

export const coreAgents = [
  {
    id: "cofounder",
    name: "Co-Founder Agent",
    description: "Strategic vision and business intent bridge",
    icon: "🤝",
    role: "Translates business goals into actionable agent tasks",
  },
  {
    id: "manager",
    name: "Manager Agent",
    description: "Workflow coordination and orchestration",
    icon: "👔",
    role: "Coordinates specialist agents and manages workflows",
  },
]
