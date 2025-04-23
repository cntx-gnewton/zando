import React, { createContext, useState, useEffect, ReactNode } from 'react';
import { getUserFromToken, isTokenExpired, GoogleUser } from '../utils/googleAuth';

interface AuthContextType {
  isAuthenticated: boolean;
  login: (token: string) => void;
  logout: () => void;
  user: GoogleUser | null;
}

const defaultAuthContext: AuthContextType = {
  isAuthenticated: false,
  login: () => {},
  logout: () => {},
  user: null
};

export const AuthContext = createContext<AuthContextType>(defaultAuthContext);

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState<GoogleUser | null>(null);

  // Check for existing token on load
  useEffect(() => {
    const token = localStorage.getItem('google_token');
    if (token && !isTokenExpired(token)) {
      const googleUser = getUserFromToken(token);
      
      if (googleUser) {
        // Add created_at if missing (first login)
        const storedCreatedAt = localStorage.getItem(`user_created_at_${googleUser.id}`);
        let createdAt: string;
        
        if (storedCreatedAt) {
          createdAt = storedCreatedAt;
        } else {
          createdAt = new Date().toISOString();
          localStorage.setItem(`user_created_at_${googleUser.id}`, createdAt);
        }
        
        // Create a new user object with the created_at information
        const userWithCreatedAt: GoogleUser = {
          ...googleUser,
          createdAt
        };
        
        setUser(userWithCreatedAt);
        setIsAuthenticated(true);
      } else {
        // Invalid token
        logout();
      }
    }
  }, []);

  const login = (token: string) => {
    const googleUser = getUserFromToken(token);
    
    if (googleUser) {
      localStorage.setItem('google_token', token);
      
      // Check if this is a first-time login
      const storedCreatedAt = localStorage.getItem(`user_created_at_${googleUser.id}`);
      let createdAt: string;
      
      if (!storedCreatedAt) {
        createdAt = new Date().toISOString();
        localStorage.setItem(`user_created_at_${googleUser.id}`, createdAt);
      } else {
        createdAt = storedCreatedAt;
      }
      
      // Create a new user object with the created_at information
      const userWithCreatedAt: GoogleUser = {
        ...googleUser,
        createdAt
      };
      
      setUser(userWithCreatedAt);
      setIsAuthenticated(true);
    }
  };

  const logout = () => {
    localStorage.removeItem('google_token');
    setIsAuthenticated(false);
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ isAuthenticated, login, logout, user }}>
      {children}
    </AuthContext.Provider>
  );
};

export default AuthProvider;