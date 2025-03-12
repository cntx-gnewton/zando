# Google Authentication Integration Guide

This directory contains a sample application that demonstrates how to integrate Google Authentication (Firebase Auth) with a FastAPI backend and React frontend. This guide explains the key components and how to adapt them for the Zando Genomic Analysis platform.

## Overview

The sample implements a complete authentication flow using Firebase Authentication, allowing users to:
1. Sign in with Google credentials
2. Obtain secure JWT tokens for API authorization
3. Access protected API endpoints with proper authentication
4. Manage user sessions across the application

## Key Components

### Backend (FastAPI Integration)

1. **JWT Authentication Middleware**
   - Located in `middleware.js` (lines 22-45)
   - Uses Firebase Admin SDK to verify tokens
   - Extracts user information from valid tokens
   - Can be adapted to FastAPI using Python Firebase Admin SDK

2. **Protected API Endpoints**
   - Example in `app.js` (line 84)
   - Shows how to require authentication for specific routes
   - Demonstrates accessing user ID from verified tokens

3. **Database Integration**
   - Shows how to associate user actions with authenticated users
   - Stores user IDs in database records

### Frontend (React Integration)

1. **Firebase Initialization**
   - Located in `static/config.js` and `static/firebase.js`
   - Shows project configuration setup
   - Handles initialization of Firebase authentication services

2. **Authentication State Management**
   - Located in `static/firebase.js` (lines 18-34)
   - Monitors user authentication state
   - Updates UI based on signed-in status

3. **Login/Logout Functionality**
   - Located in `static/firebase.js` (lines 36-73)
   - Implements Google sign-in popup
   - Handles sign-out process
   - Manages authentication errors

4. **Authenticated API Requests**
   - Located in `static/firebase.js` (lines 75-104)
   - Shows how to obtain current user's ID token
   - Demonstrates adding the token to API requests
   - Handles authentication errors in requests

## FastAPI Implementation Steps

1. **Install Required Dependencies**
   ```bash
   pip install fastapi firebase-admin python-jose
   ```

2. **Initialize Firebase Admin in FastAPI**
   ```python
   import firebase_admin
   from firebase_admin import credentials, auth

   # Initialize Firebase Admin SDK
   cred = credentials.Certificate("path/to/serviceAccountKey.json")
   firebase_admin.initialize_app(cred)
   ```

3. **Create Authentication Middleware**
   ```python
   from fastapi import Depends, HTTPException, status
   from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

   security = HTTPBearer()

   async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
       token = credentials.credentials
       try:
           # Verify the token
           decoded_token = auth.verify_id_token(token)
           # Return the token information
           return decoded_token
       except Exception as e:
           raise HTTPException(
               status_code=status.HTTP_401_UNAUTHORIZED,
               detail=f"Invalid authentication credentials: {e}"
           )
   ```

4. **Protect API Endpoints**
   ```python
   from fastapi import APIRouter, Depends

   router = APIRouter()

   @router.post("/protected-endpoint")
   async def protected_endpoint(token_data: dict = Depends(verify_token)):
       user_id = token_data.get("uid")
       # Use user_id in your application logic
       return {"message": f"Hello user {user_id}"}
   ```

## React Implementation Steps

1. **Install Required Dependencies**
   ```bash
   npm install firebase
   ```

2. **Create Firebase Configuration**
   ```javascript
   // src/firebaseConfig.js
   import { initializeApp } from 'firebase/app';
   import { getAuth } from 'firebase/auth';

   const firebaseConfig = {
     apiKey: process.env.REACT_APP_FIREBASE_API_KEY,
     authDomain: process.env.REACT_APP_FIREBASE_AUTH_DOMAIN,
     projectId: process.env.REACT_APP_FIREBASE_PROJECT_ID,
   };

   const app = initializeApp(firebaseConfig);
   export const auth = getAuth(app);
   ```

3. **Create Authentication Context**
   ```javascript
   // src/contexts/AuthContext.tsx
   import React, { createContext, useContext, useEffect, useState } from 'react';
   import { 
     GoogleAuthProvider, 
     signInWithPopup, 
     signOut, 
     onAuthStateChanged, 
     User 
   } from 'firebase/auth';
   import { auth } from '../firebaseConfig';

   const AuthContext = createContext<{
     currentUser: User | null;
     signInWithGoogle: () => Promise<void>;
     logout: () => Promise<void>;
     getIdToken: () => Promise<string | null>;
   }>({
     currentUser: null,
     signInWithGoogle: async () => {},
     logout: async () => {},
     getIdToken: async () => null,
   });

   export function useAuth() {
     return useContext(AuthContext);
   }

   export function AuthProvider({ children }: { children: React.ReactNode }) {
     const [currentUser, setCurrentUser] = useState<User | null>(null);
     const [loading, setLoading] = useState(true);

     const signInWithGoogle = async () => {
       const provider = new GoogleAuthProvider();
       try {
         await signInWithPopup(auth, provider);
       } catch (error) {
         console.error('Error signing in:', error);
       }
     };

     const logout = async () => {
       try {
         await signOut(auth);
       } catch (error) {
         console.error('Error signing out:', error);
       }
     };

     const getIdToken = async () => {
       if (!currentUser) return null;
       try {
         return await currentUser.getIdToken();
       } catch (error) {
         console.error('Error getting ID token:', error);
         return null;
       }
     };

     useEffect(() => {
       const unsubscribe = onAuthStateChanged(auth, (user) => {
         setCurrentUser(user);
         setLoading(false);
       });

       return unsubscribe;
     }, []);

     const value = {
       currentUser,
       signInWithGoogle,
       logout,
       getIdToken,
     };

     return (
       <AuthContext.Provider value={value}>
         {!loading && children}
       </AuthContext.Provider>
     );
   }
   ```

4. **Create API Service with Auth Integration**
   ```javascript
   // src/api/apiClient.ts
   import axios from 'axios';
   import { useAuth } from '../contexts/AuthContext';

   const createAuthenticatedApiClient = () => {
     const { getIdToken } = useAuth();
     
     const apiClient = axios.create({
       baseURL: process.env.REACT_APP_API_URL || '/api/v1',
       timeout: 30000,
     });

     apiClient.interceptors.request.use(async (config) => {
       const token = await getIdToken();
       if (token) {
         config.headers.Authorization = `Bearer ${token}`;
       }
       return config;
     });

     return apiClient;
   };

   export const useApiClient = () => {
     return createAuthenticatedApiClient();
   };
   ```

## Security Considerations

1. **Token Verification**
   - Always verify tokens on the server side
   - Never trust client-side authentication alone
   - Validate token signature, expiration, and issuer

2. **HTTPS**
   - Always use HTTPS in production
   - Protect tokens in transit

3. **Token Storage**
   - Firebase handles token storage securely
   - Don't store tokens in local storage or cookies manually

4. **CORS Configuration**
   - Configure proper CORS settings on your FastAPI backend
   - Only allow known origins to make authenticated requests

5. **Authorization**
   - Authentication verifies identity, but you still need authorization logic
   - Implement role-based access control as needed

## Getting Started

1. Create a Firebase project at https://console.firebase.google.com/
2. Enable Google Sign-In in the Firebase Authentication section
3. Create a Service Account and download the private key JSON file
4. Update environment variables with Firebase configuration
5. Implement the authentication middleware in your FastAPI app
6. Set up the React authentication context and components
7. Test the authentication flow end-to-end

## Resources

- [Firebase Authentication Documentation](https://firebase.google.com/docs/auth)
- [FastAPI Security Documentation](https://fastapi.tiangolo.com/tutorial/security/)
- [Firebase Admin SDK for Python](https://firebase.google.com/docs/admin/setup#python)
- [React Firebase Hooks](https://github.com/CSFrequency/react-firebase-hooks)