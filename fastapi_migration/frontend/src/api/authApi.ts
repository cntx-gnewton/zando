import axiosInstance from './axiosConfig';

/**
 * Types for authentication requests and responses
 */
export interface LoginRequest {
  username: string;
  password: string;
}

export interface RegisterRequest {
  username: string;
  email: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface UserResponse {
  id: number;
  username: string;
  email: string;
  is_active: boolean;
  created_at: string;
}

/**
 * API client for authentication operations
 */
export const authApi = {
  /**
   * Login with username and password
   * 
   * @param credentials - username and password
   * @returns TokenResponse with access_token and token_type
   */
  login: async (credentials: LoginRequest): Promise<TokenResponse> => {
    // Convert credentials to form data format required by OAuth2
    const formData = new URLSearchParams();
    formData.append('username', credentials.username);
    formData.append('password', credentials.password);
    
    console.log('Logging in at:', '/auth/login');
    
    const response = await axiosInstance.post(
      '/auth/login',
      formData.toString(),
      {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      }
    );
    
    console.log('Login response:', response.data);
    return response.data;
  },
  
  /**
   * Register a new user
   * 
   * @param userData - user registration data
   * @returns UserResponse with the newly created user
   */
  register: async (userData: RegisterRequest): Promise<UserResponse> => {
    console.log('Registering at:', '/auth/register');
    
    const response = await axiosInstance.post('/auth/register', userData);
    console.log('Register response:', response.data);
    return response.data;
  },
  
  /**
   * Get current user profile information
   * 
   * @returns User information
   */
  getProfile: async (): Promise<UserResponse> => {
    console.log('Getting profile from:', '/auth/me');
    
    const response = await axiosInstance.get('/auth/me');
    
    console.log('Profile response:', response.data);
    return response.data;
  },
  
  /**
   * Update current user profile information
   * 
   * @param userData - user data to update
   * @returns Updated user information
   */
  updateProfile: async (userData: Partial<RegisterRequest>): Promise<UserResponse> => {
    console.log('Updating profile at:', '/auth/me');
    
    const response = await axiosInstance.put('/auth/me', userData);
    
    console.log('Update profile response:', response.data);
    return response.data;
  },
  
  /**
   * Logout the current user (client-side only)
   */
  logout: () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
  },
  
  /**
   * Check if the user is currently authenticated
   * 
   * @returns true if authenticated, false otherwise
   */
  isAuthenticated: (): boolean => {
    return localStorage.getItem('token') !== null;
  }
};

export default authApi;