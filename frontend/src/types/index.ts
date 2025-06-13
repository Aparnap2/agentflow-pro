export interface User {
  id: string | number;
  name: string;
  email: string;
  company: string;
  plan: string;
  status: 'active' | 'inactive' | 'suspended' | 'trial';
  lastLogin: string;
  agentsDeployed?: number;
  monthlyUsage?: string;
  joinDate?: string;
  totalTasks?: number;
  successRate?: number;
  role: 'admin' | 'user' | 'viewer';
  createdAt: string;
}

export interface SystemMetrics {
  totalUsers: number;
  activeAgents: number;
  systemHealth: number;
  totalRevenue: number;
}
