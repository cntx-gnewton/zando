import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { authApi, LoginRequest, RegisterRequest, UserResponse } from '../api/authApi';

// Define the shape of our authentication context
interface AuthContextType {
  user: UserResponse | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  login: (credentials: LoginRequest) => Promise<void>;
  register: (userData: RegisterRequest) => Promise<void>;
  logout: () => void;
  updateProfile: (userData: Partial<RegisterRequest>) => Promise<void>;
}

// Create the context with a default value
const AuthContext = createContext<AuthContextType>({
  user: null,
  isAuthenticated: false,
  isLoading: true,
  error: null,
  login: async () => {},
  register: async () => {},
  logout: () => {},
  updateProfile: async () => {},
});

// Custom hook to use the auth context
export const useAuth = () => useContext(AuthContext);

// Provider component that wraps the app and makes auth available
export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<UserResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Check if user is logged in on component mount
    const initAuth = async () => {
      const token = localStorage.getItem('token');
      const storedUser = localStorage.getItem('user');
      
      if (token && storedUser) {
        try {
          setUser(JSON.parse(storedUser));
          // Optionally verify the token with the server
          try {
            const profile = await authApi.getProfile();
            setUser(profile);
            localStorage.setItem('user', JSON.stringify(profile));
          } catch (profileErr) {
            console.error('Failed to fetch profile:', profileErr);
            // If token is invalid, log the user out
            if (profileErr.response && profileErr.response.status === 401) {
              logout();
            }
          }
        } catch (e) {
          console.error('Error parsing stored user:', e);
          logout();
        }
      }
      
      setIsLoading(false);
    };
    
    initAuth();
  }, []);

  // Login function
  const login = async (credentials: LoginRequest) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await authApi.login(credentials);
      // Store the token
      localStorage.setItem('token', response.access_token);
      
      // Fetch user profile
      const profile = await authApi.getProfile();
      setUser(profile);
      // Store user data
      localStorage.setItem('user', JSON.stringify(profile));
    } catch (err) {
      console.error('Login error:', err);
      setError(err.response?.data?.detail || 'Login failed. Please check your credentials.');
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  // Register function
  const register = async (userData: RegisterRequest) => {
    setIsLoading(true);
    setError(null);
    
    try {
      // Register the user
      const newUser = await authApi.register(userData);
      setUser(newUser);
      
      // Login after registration
      await login({
        username: userData.username,
        password: userData.password,
      });
    } catch (err) {
      console.error('Registration error:', err);
      setError(err.response?.data?.detail || 'Registration failed. Please try again.');
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  // Logout function
  const logout = () => {
    // Remove token and user from storage
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    // Update state
    setUser(null);
    setError(null);
  };

  // Update profile function
  const updateProfile = async (userData: Partial<RegisterRequest>) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const updatedUser = await authApi.updateProfile(userData);
      setUser(updatedUser);
      localStorage.setItem('user', JSON.stringify(updatedUser));
    } catch (err) {
      console.error('Profile update error:', err);
      setError(err.response?.data?.detail || 'Failed to update profile. Please try again.');
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  // Provide the context value to children
  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: !!user,
        isLoading,
        error,
        login,
        register,
        logout,
        updateProfile,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export default AuthContext;