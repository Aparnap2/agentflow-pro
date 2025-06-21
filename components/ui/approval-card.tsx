"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"
import { CheckCircle, XCircle, Clock, DollarSign, AlertTriangle, Target } from "lucide-react"
import type { ResearchPlan } from "@/types/workflow"

interface ApprovalCardProps {
  plan: ResearchPlan
  onApprove: (planId: string) => void
  onReject: (planId: string) => void
  onRequestChanges?: (planId: string, feedback: string) => void
}

export function ApprovalCard({ plan, onApprove, onReject, onRequestChanges }: ApprovalCardProps) {
  return (
    <Card className="border-2 border-blue-200 bg-blue-50 dark:bg-blue-950 max-w-2xl">
      <CardHeader>
        <div className="flex items-start justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              <Target className="w-5 h-5 text-blue-600" />
              Strategic Plan Approval Required
            </CardTitle>
            <p className="text-sm text-muted-foreground mt-1">Co-Founder Agent has prepared a detailed plan</p>
          </div>
          <Badge variant={plan.priority === "urgent" ? "destructive" : "secondary"}>{plan.priority}</Badge>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        <div>
          <h4 className="font-semibold text-lg">{plan.title}</h4>
          <p className="text-sm text-muted-foreground mt-1">{plan.description}</p>
        </div>

        <Separator />

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <h5 className="font-medium text-sm mb-2">Research Findings</h5>
            <ul className="text-xs space-y-1">
              {plan.researchFindings.slice(0, 3).map((finding, index) => (
                <li key={index} className="flex items-start gap-2">
                  <div className="w-1 h-1 bg-blue-500 rounded-full mt-2 flex-shrink-0"></div>
                  <span>{finding}</span>
                </li>
              ))}
              {plan.researchFindings.length > 3 && (
                <li className="text-muted-foreground">+{plan.researchFindings.length - 3} more findings...</li>
              )}
            </ul>
          </div>

          <div>
            <h5 className="font-medium text-sm mb-2">Proposed Actions</h5>
            <ul className="text-xs space-y-1">
              {plan.proposedActions.slice(0, 3).map((action, index) => (
                <li key={index} className="flex items-start gap-2">
                  <div className="w-1 h-1 bg-green-500 rounded-full mt-2 flex-shrink-0"></div>
                  <span>{action}</span>
                </li>
              ))}
              {plan.proposedActions.length > 3 && (
                <li className="text-muted-foreground">+{plan.proposedActions.length - 3} more actions...</li>
              )}
            </ul>
          </div>
        </div>

        <Separator />

        <div className="grid grid-cols-3 gap-4 text-center">
          <div>
            <div className="flex items-center justify-center gap-1 mb-1">
              <Clock className="w-3 h-3 text-blue-600" />
              <span className="text-xs font-medium">Timeline</span>
            </div>
            <p className="text-sm font-semibold">{plan.timeline}</p>
          </div>
          <div>
            <div className="flex items-center justify-center gap-1 mb-1">
              <DollarSign className="w-3 h-3 text-green-600" />
              <span className="text-xs font-medium">Budget</span>
            </div>
            <p className="text-sm font-semibold">${plan.budget.toLocaleString()}</p>
          </div>
          <div>
            <div className="flex items-center justify-center gap-1 mb-1">
              <AlertTriangle className="w-3 h-3 text-orange-600" />
              <span className="text-xs font-medium">Risks</span>
            </div>
            <p className="text-sm font-semibold">{plan.risks.length} identified</p>
          </div>
        </div>

        <div>
          <h5 className="font-medium text-sm mb-2">Expected Outcomes</h5>
          <div className="flex flex-wrap gap-1">
            {plan.expectedOutcomes.map((outcome, index) => (
              <Badge key={index} variant="outline" className="text-xs">
                {outcome}
              </Badge>
            ))}
          </div>
        </div>

        <Separator />

        <div className="flex gap-3">
          <Button onClick={() => onApprove(plan.id)} className="flex-1 bg-green-600 hover:bg-green-700">
            <CheckCircle className="w-4 h-4 mr-2" />
            Approve & Execute
          </Button>
          <Button variant="outline" onClick={() => onReject(plan.id)} className="flex-1">
            <XCircle className="w-4 h-4 mr-2" />
            Reject Plan
          </Button>
        </div>

        <p className="text-xs text-muted-foreground text-center">
          Approving will trigger Manager Agent to orchestrate execution across specialist agents
        </p>
      </CardContent>
    </Card>
  )
}
