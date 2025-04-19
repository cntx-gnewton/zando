/**
 * Utility functions for working with Google authentication
 */

/**
 * Decode a JWT token to get the payload
 * @param token - The JWT token to decode
 * @returns The decoded payload or null if invalid
 */
export const decodeToken = (token: string): any => {
  try {
    // JWT tokens consist of three parts separated by dots: header.payload.signature
    const base64Url = token.split('.')[1];
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const jsonPayload = decodeURIComponent(
      window
        .atob(base64)
        .split('')
        .map(function(c) {
          return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
        })
        .join('')
    );

    return JSON.parse(jsonPayload);
  } catch (error) {
    console.error('Error decoding token:', error);
    return null;
  }
};

/**
 * Interface for Google user information
 */
export interface GoogleUser {
  id: string;
  email: string;
  name: string;
  picture: string;
  givenName: string;
  familyName: string;
  createdAt?: string;
}

/**
 * Extract user information from a Google JWT token
 * @param token - The Google JWT token
 * @returns User information object
 */
export const getUserFromToken = (token: string): GoogleUser | null => {
  const decoded = decodeToken(token);
  
  if (!decoded) {
    return null;
  }
  
  return {
    id: decoded.sub,
    email: decoded.email,
    name: decoded.name,
    picture: decoded.picture,
    givenName: decoded.given_name,
    familyName: decoded.family_name
  };
};

/**
 * Check if a token has expired
 * @param token - The JWT token
 * @returns True if expired, false otherwise
 */
export const isTokenExpired = (token: string): boolean => {
  const decoded = decodeToken(token);
  
  if (!decoded || !decoded.exp) {
    return true;
  }
  
  // exp is in seconds, Date.now() is in milliseconds
  const currentTime = Date.now() / 1000;
  return decoded.exp < currentTime;
};