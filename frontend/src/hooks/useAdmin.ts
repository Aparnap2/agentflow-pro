import { useState, useEffect, useCallback } from 'react';
import { adminApi } from '../services/api';
import { User } from '../types';

interface SystemMetrics {
  totalUsers: number;
  activeUsers: number;
  totalAgents: number;
  activeAgents: number;
  totalOrchestrations: number;
  runningOrchestrations: number;
  systemHealth: number;
  uptime: string;
  totalRevenue: number;
  monthlyGrowth: number;
  supportTickets: number;
  criticalAlerts: number;
}

export const useAdmin = () => {
  const [systemMetrics, setSystemMetrics] = useState<SystemMetrics | null>(null);
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [currentPage, setCurrentPage] = useState<number>(1);
  const [totalPages, setTotalPages] = useState<number>(1);
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [filterStatus, setFilterStatus] = useState<string>('all');

  // Fetch system metrics
  const fetchSystemMetrics = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await adminApi.getSystemMetrics();
      setSystemMetrics(data);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch system metrics');
      console.error('Error fetching system metrics:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  // Fetch users with pagination and filters
  const fetchUsers = useCallback(async (page: number = 1, search: string = searchTerm, status: string = filterStatus) => {
    setLoading(true);
    setError(null);
    try {
      const params: any = {
        page,
        limit: 10,
      };
      
      if (search) params.search = search;
      if (status !== 'all') params.status = status;
      
      const { data, total, pages } = await adminApi.getUsers(params);
      setUsers(data);
      setTotalPages(pages);
      setCurrentPage(page);
      return data;
    } catch (err: any) {
      setError(err.message || 'Failed to fetch users');
      console.error('Error fetching users:', err);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [searchTerm, filterStatus]);

  // Create a new user
  const createUser = useCallback(async (userData: Omit<User, 'id' | 'createdAt' | 'lastLogin'>) => {
    setLoading(true);
    setError(null);
    try {
      const newUser = await adminApi.createUser(userData);
      setUsers(prev => [newUser, ...prev]);
      return newUser;
    } catch (err: any) {
      setError(err.message || 'Failed to create user');
      console.error('Error creating user:', err);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  // Update a user
  const updateUser = useCallback(async (userId: string, userData: Partial<User>) => {
    setLoading(true);
    setError(null);
    try {
      const updatedUser = await adminApi.updateUser(userId, userData);
      setUsers(prev => 
        prev.map(user => user.id === userId ? { ...user, ...updatedUser } : user)
      );
      return updatedUser;
    } catch (err: any) {
      setError(err.message || 'Failed to update user');
      console.error('Error updating user:', err);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  // Delete a user
  const deleteUser = useCallback(async (userId: string) => {
    setLoading(true);
    setError(null);
    try {
      await adminApi.deleteUser(userId);
      setUsers(prev => prev.filter(user => user.id !== userId));
    } catch (err: any) {
      setError(err.message || 'Failed to delete user');
      console.error('Error deleting user:', err);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  // Initial data fetch
  useEffect(() => {
    fetchSystemMetrics();
    fetchUsers(1);
  }, [fetchSystemMetrics, fetchUsers]);

  return {
    // State
    systemMetrics,
    users,
    loading,
    error,
    currentPage,
    totalPages,
    searchTerm,
    filterStatus,
    
    // Actions
    setSearchTerm,
    setFilterStatus,
    setCurrentPage,
    fetchSystemMetrics,
    fetchUsers,
    createUser,
    updateUser,
    deleteUser,
  };
};

export default useAdmin;
