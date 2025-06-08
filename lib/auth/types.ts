import { DefaultSession, DefaultUser } from 'next-auth';
import { JWT } from 'next-auth/jwt';

declare module 'next-auth' {
  /**
   * Extend the built-in session types
   */
  interface Session {
    user: {
      id: string;
      // Add any other custom fields you add to your user object
    } & DefaultSession['user'];
    accessToken?: string;
  }

  /**
   * Extend the built-in user types
   */
  interface User extends DefaultUser {
    // Add any additional fields that your provider returns
  }
}

declare module 'next-auth/jwt' {
  /**
   * Extend the built-in JWT types
   */
  interface JWT {
    id: string;
    accessToken?: string;
  }
}
