import { auth } from '@/auth';

export async function getCurrentUser() {
  const session = await auth();
  return session?.user;
}

export async function getCurrentSession() {
  return await auth();
}

export async function getCurrentUserId() {
  const session = await auth();
  return session?.user?.id;
}

export async function getCurrentUserEmail() {
  const session = await auth();
  return session?.user?.email;
}

export async function isAuthenticated() {
  const session = await auth();
  return !!session?.user;
}
