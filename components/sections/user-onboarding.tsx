"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { CheckCircle, ArrowRight, Building, Target, Users, Zap } from "lucide-react"

interface OnboardingStep {
  id: string
  title: string
  description: string
  completed: boolean
}

export function UserOnboarding() {
  const [currentStep, setCurrentStep] = useState(0)
  const [formData, setFormData] = useState({
    companyName: "",
    industry: "",
    teamSize: "",
    businessGoals: "",
    currentChallenges: "",
    automationPriorities: [] as string[],
  })

  const steps: OnboardingStep[] = [
    {
      id: "welcome",
      title: "Welcome to AgentFlow Pro",
      description: "Let's set up your virtual office and AI team",
      completed: false,
    },
    {
      id: "company-info",
      title: "Company Information",
      description: "Tell us about your business",
      completed: false,
    },
    {
      id: "goals-challenges",
      title: "Goals & Challenges",
      description: "What do you want to achieve?",
      completed: false,
    },
    {
      id: "team-setup",
      title: "Virtual Team Setup",
      description: "Configure your AI agents",
      completed: false,
    },
    {
      id: "complete",
      title: "Setup Complete",
      description: "Your virtual office is ready!",
      completed: false,
    },
  ]

  const automationOptions = [
    "Lead Management & CRM",
    "Email Marketing Automation",
    "Invoice & Payment Processing",
    "Appointment Scheduling",
    "Social Media Management",
    "HR & Time Tracking",
    "Administrative Tasks",
    "Customer Review Management",
  ]

  const handleNext = () => {
    if (currentStep < steps.length - 1) {
      setCurrentStep(currentStep + 1)
    }
  }

  const handlePrevious = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1)
    }
  }

  const toggleAutomationPriority = (option: string) => {
    setFormData((prev) => ({
      ...prev,
      automationPriorities: prev.automationPriorities.includes(option)
        ? prev.automationPriorities.filter((p) => p !== option)
        : [...prev.automationPriorities, option],
    }))
  }

  const progress = ((currentStep + 1) / steps.length) * 100

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="text-center">
        <h2 className="text-3xl font-bold">Welcome to Your Virtual Office</h2>
        <p className="text-muted-foreground mt-2">Let's set up your AI-powered team in just a few steps</p>
      </div>

      {/* Progress Bar */}
      <Card>
        <CardContent className="p-6">
          <div className="space-y-4">
            <div className="flex justify-between text-sm">
              <span>Setup Progress</span>
              <span>{Math.round(progress)}% Complete</span>
            </div>
            <Progress value={progress} className="h-2" />
            <div className="flex justify-between">
              {steps.map((step, index) => (
                <div
                  key={step.id}
                  className={`flex flex-col items-center ${index <= currentStep ? "text-blue-600" : "text-muted-foreground"}`}
                >
                  <div
                    className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-semibold ${
                      index < currentStep
                        ? "bg-green-500 text-white"
                        : index === currentStep
                          ? "bg-blue-500 text-white"
                          : "bg-gray-200"
                    }`}
                  >
                    {index < currentStep ? <CheckCircle className="w-4 h-4" /> : index + 1}
                  </div>
                  <span className="text-xs mt-1 text-center max-w-20">{step.title}</span>
                </div>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Step Content */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            {currentStep === 0 && <Zap className="w-5 h-5" />}
            {currentStep === 1 && <Building className="w-5 h-5" />}
            {currentStep === 2 && <Target className="w-5 h-5" />}
            {currentStep === 3 && <Users className="w-5 h-5" />}
            {currentStep === 4 && <CheckCircle className="w-5 h-5" />}
            {steps[currentStep].title}
          </CardTitle>
          <p className="text-muted-foreground">{steps[currentStep].description}</p>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Welcome Step */}
          {currentStep === 0 && (
            <div className="text-center space-y-6">
              <div className="w-24 h-24 bg-gradient-to-r from-blue-600 to-purple-600 rounded-full flex items-center justify-center mx-auto">
                <Users className="w-12 h-12 text-white" />
              </div>
              <div>
                <h3 className="text-xl font-semibold mb-2">Your AI-Powered Virtual Office</h3>
                <p className="text-muted-foreground">
                  AgentFlow Pro creates a virtual team of AI agents that work together to automate your business tasks.
                  You'll have a Co-Founder Agent for strategy, a Manager Agent for coordination, and specialist agents
                  for specific tasks.
                </p>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="p-4 border rounded-lg">
                  <div className="text-2xl mb-2">🤝</div>
                  <h4 className="font-semibold">Co-Founder Agent</h4>
                  <p className="text-sm text-muted-foreground">Strategic partner for business planning</p>
                </div>
                <div className="p-4 border rounded-lg">
                  <div className="text-2xl mb-2">👔</div>
                  <h4 className="font-semibold">Manager Agent</h4>
                  <p className="text-sm text-muted-foreground">Coordinates team and asks for approvals</p>
                </div>
                <div className="p-4 border rounded-lg">
                  <div className="text-2xl mb-2">⚡</div>
                  <h4 className="font-semibold">Specialist Agents</h4>
                  <p className="text-sm text-muted-foreground">Execute specific business tasks</p>
                </div>
              </div>
            </div>
          )}

          {/* Company Info Step */}
          {currentStep === 1 && (
            <div className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="company-name">Company Name</Label>
                  <Input
                    id="company-name"
                    placeholder="Your Company Name"
                    value={formData.companyName}
                    onChange={(e) => setFormData((prev) => ({ ...prev, companyName: e.target.value }))}
                  />
                </div>
                <div>
                  <Label>Industry</Label>
                  <Select
                    value={formData.industry}
                    onValueChange={(value) => setFormData((prev) => ({ ...prev, industry: value }))}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select your industry" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="saas">SaaS/Technology</SelectItem>
                      <SelectItem value="ecommerce">E-commerce</SelectItem>
                      <SelectItem value="consulting">Consulting</SelectItem>
                      <SelectItem value="agency">Marketing Agency</SelectItem>
                      <SelectItem value="healthcare">Healthcare</SelectItem>
                      <SelectItem value="finance">Finance</SelectItem>
                      <SelectItem value="education">Education</SelectItem>
                      <SelectItem value="other">Other</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
              <div>
                <Label>Team Size</Label>
                <Select
                  value={formData.teamSize}
                  onValueChange={(value) => setFormData((prev) => ({ ...prev, teamSize: value }))}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="How many people in your team?" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="1-5">1-5 people</SelectItem>
                    <SelectItem value="6-20">6-20 people</SelectItem>
                    <SelectItem value="21-50">21-50 people</SelectItem>
                    <SelectItem value="51+">51+ people</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
          )}

          {/* Goals & Challenges Step */}
          {currentStep === 2 && (
            <div className="space-y-4">
              <div>
                <Label htmlFor="business-goals">Business Goals</Label>
                <Textarea
                  id="business-goals"
                  placeholder="What are your main business objectives for this year?"
                  value={formData.businessGoals}
                  onChange={(e) => setFormData((prev) => ({ ...prev, businessGoals: e.target.value }))}
                />
              </div>
              <div>
                <Label htmlFor="current-challenges">Current Challenges</Label>
                <Textarea
                  id="current-challenges"
                  placeholder="What repetitive tasks are taking up too much of your team's time?"
                  value={formData.currentChallenges}
                  onChange={(e) => setFormData((prev) => ({ ...prev, currentChallenges: e.target.value }))}
                />
              </div>
              <div>
                <Label>Automation Priorities</Label>
                <p className="text-sm text-muted-foreground mb-3">Select the areas you'd like to automate first:</p>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                  {automationOptions.map((option) => (
                    <div
                      key={option}
                      className={`p-3 border rounded-lg cursor-pointer transition-colors ${
                        formData.automationPriorities.includes(option)
                          ? "border-blue-500 bg-blue-50 dark:bg-blue-950"
                          : "hover:bg-slate-50"
                      }`}
                      onClick={() => toggleAutomationPriority(option)}
                    >
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-medium">{option}</span>
                        {formData.automationPriorities.includes(option) && <Badge variant="secondary">Selected</Badge>}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Team Setup Step */}
          {currentStep === 3 && (
            <div className="space-y-6">
              <div className="text-center">
                <h3 className="text-xl font-semibold mb-2">Your Virtual Team is Being Configured</h3>
                <p className="text-muted-foreground">
                  Based on your priorities, we're setting up the perfect AI team for your business.
                </p>
              </div>

              <div className="space-y-4">
                <div className="p-4 border rounded-lg bg-green-50 dark:bg-green-950">
                  <div className="flex items-center gap-3">
                    <CheckCircle className="w-5 h-5 text-green-600" />
                    <div>
                      <h4 className="font-semibold">Co-Founder Agent - Alex Chen</h4>
                      <p className="text-sm text-muted-foreground">
                        Strategic partner configured with your business context
                      </p>
                    </div>
                  </div>
                </div>

                <div className="p-4 border rounded-lg bg-green-50 dark:bg-green-950">
                  <div className="flex items-center gap-3">
                    <CheckCircle className="w-5 h-5 text-green-600" />
                    <div>
                      <h4 className="font-semibold">Manager Agent - Sarah Kim</h4>
                      <p className="text-sm text-muted-foreground">Team coordinator ready to manage workflows</p>
                    </div>
                  </div>
                </div>

                {formData.automationPriorities.slice(0, 3).map((priority, index) => (
                  <div key={priority} className="p-4 border rounded-lg bg-blue-50 dark:bg-blue-950">
                    <div className="flex items-center gap-3">
                      <div className="w-5 h-5 bg-blue-600 rounded-full flex items-center justify-center">
                        <span className="text-white text-xs">{index + 1}</span>
                      </div>
                      <div>
                        <h4 className="font-semibold">Specialist Agent</h4>
                        <p className="text-sm text-muted-foreground">{priority} automation ready</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Complete Step */}
          {currentStep === 4 && (
            <div className="text-center space-y-6">
              <div className="w-24 h-24 bg-green-500 rounded-full flex items-center justify-center mx-auto">
                <CheckCircle className="w-12 h-12 text-white" />
              </div>
              <div>
                <h3 className="text-xl font-semibold mb-2">Welcome to Your Virtual Office!</h3>
                <p className="text-muted-foreground">
                  Your AI team is ready to start working. You can now chat with your Co-Founder Agent to discuss
                  business strategies and approve tasks from your Manager Agent.
                </p>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="p-4 border rounded-lg">
                  <h4 className="font-semibold mb-2">Next Steps:</h4>
                  <ul className="text-sm text-muted-foreground space-y-1">
                    <li>• Chat with Alex (Co-Founder) about your goals</li>
                    <li>• Review task assignments from Sarah (Manager)</li>
                    <li>• Monitor your team's progress</li>
                    <li>• Approve or reject task requests</li>
                  </ul>
                </div>
                <div className="p-4 border rounded-lg">
                  <h4 className="font-semibold mb-2">Your Team:</h4>
                  <ul className="text-sm text-muted-foreground space-y-1">
                    <li>• 🤝 Alex Chen (Co-Founder)</li>
                    <li>• 👔 Sarah Kim (Manager)</li>
                    <li>• ⚡ {formData.automationPriorities.length} Specialists</li>
                  </ul>
                </div>
              </div>
            </div>
          )}

          {/* Navigation */}
          <div className="flex justify-between pt-6">
            <Button variant="outline" onClick={handlePrevious} disabled={currentStep === 0}>
              Previous
            </Button>
            <Button
              onClick={handleNext}
              disabled={currentStep === steps.length - 1}
              className="bg-gradient-to-r from-blue-600 to-purple-600"
            >
              {currentStep === steps.length - 2 ? "Complete Setup" : "Next"}
              <ArrowRight className="w-4 h-4 ml-2" />
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
