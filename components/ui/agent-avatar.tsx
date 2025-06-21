import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"

interface AgentAvatarProps {
  agent: {
    name: string
    avatar: string
    status: "active" | "idle" | "working" | "waiting_approval"
  }
  size?: "sm" | "md" | "lg"
  showStatus?: boolean
}

export function AgentAvatar({ agent, size = "md", showStatus = true }: AgentAvatarProps) {
  const sizeClasses = {
    sm: "w-8 h-8",
    md: "w-12 h-12",
    lg: "w-16 h-16",
  }

  const statusColors = {
    active: "bg-green-500",
    idle: "bg-gray-400",
    working: "bg-blue-500",
    waiting_approval: "bg-yellow-500",
  }

  return (
    <div className="relative">
      <Avatar className={sizeClasses[size]}>
        <AvatarImage src={agent.avatar || "/placeholder.svg"} alt={agent.name} />
        <AvatarFallback>
          {agent.name
            .split(" ")
            .map((n) => n[0])
            .join("")}
        </AvatarFallback>
      </Avatar>
      {showStatus && (
        <div
          className={`absolute -bottom-1 -right-1 w-3 h-3 rounded-full border-2 border-white ${statusColors[agent.status]}`}
        ></div>
      )}
    </div>
  )
}
