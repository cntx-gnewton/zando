# Zando Genomic Analysis Development Guide

This guide provides instructions for setting up the development environment and working on the Zando Genomic Analysis platform. The application consists of a FastAPI backend and a React frontend.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Project Structure](#project-structure)
- [Backend Development](#backend-development)
  - [Setting Up the Backend](#setting-up-the-backend)
  - [Running the Backend](#running-the-backend)
  - [API Endpoints](#api-endpoints)
- [Frontend Development](#frontend-development)
  - [Setting Up the Frontend](#setting-up-the-frontend)
  - [Running the Frontend](#running-the-frontend)
  - [Frontend Structure](#frontend-structure)
  - [Making Changes](#making-changes)
  - [Adding New Components](#adding-new-components)
  - [Implementing Authentication](#implementing-authentication)
  - [Styling Guidelines](#styling-guidelines)
- [Testing](#testing)
- [Deployment](#deployment)
- [Troubleshooting](#troubleshooting)

## Prerequisites

Before you begin, make sure you have the following installed:

- **Python 3.8+** - For the backend
- **Node.js 16+** - For the frontend
- **Docker** (optional) - For containerized development/deployment
- **PostgreSQL** - For database development

## Project Structure

The project is organized into two main directories:

```
/fastapi_migration/
  ├── backend/         # FastAPI backend
  │   ├── app/         # Application code
  │   ├── main.py      # Entry point
  │   └── requirements.txt
  │
  ├── frontend/        # React frontend
  │   ├── public/      # Static assets
  │   ├── src/         # React source code
  │   └── package.json # Dependencies
  │
  └── docker-compose.yml  # Development environment setup
```

## Backend Development

### Setting Up the Backend

1. Navigate to the backend directory:
   ```bash
   cd zando/backend
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the backend directory with the following environment variables:
   ```
   # Database settings
   POSTGRES_SERVER=localhost
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=postgres
   POSTGRES_DB=zando
   POSTGRES_PORT=5432
   
   # Security settings
   SECRET_KEY=yoursecretkey
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   
   # File storage settings
   CACHE_DIR=./cache
   REPORTS_DIR=./reports
   UPLOADS_DIR=./uploads
   CACHE_EXPIRY_DAYS=7
   ```

### Running the Backend

1. Start the backend server:
   ```bash
   uvicorn main:app --reload --port 8000
   ```

2. The API will be available at `http://localhost:8000`
   - Interactive API documentation: `http://localhost:8000/docs`
   - Alternative API documentation: `http://localhost:8000/redoc`

### API Endpoints

The backend provides several API endpoints grouped by functionality:

- `/api/v1/auth/*` - Authentication endpoints
- `/api/v1/dna/*` - DNA file upload and management
- `/api/v1/analysis/*` - Genetic analysis processing
- `/api/v1/reports/*` - Report generation and retrieval
- `/api/v1/cache/*` - Cache management
- `/api/v1/admin/*` - Admin operations

For a complete list of endpoints, refer to the API documentation at `/docs`.

## Frontend Development

### Setting Up the Frontend

1. Navigate to the frontend directory:
   ```bash
   cd zando/frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Create a `.env` file in the frontend directory with the following environment variables:
   ```
   REACT_APP_API_URL=http://localhost:8000/api/v1
   REACT_APP_USE_MOCK_DATA=false
   ```

### Running the Frontend

1. Start the development server:
   ```bash
   npm start
   ```

2. The frontend will be available at `http://localhost:3000`

### Frontend Structure

The frontend is structured as follows:

```
/src/
  ├── api/           # API service clients
  ├── components/    # Reusable React components
  │   ├── auth/      # Authentication components
  │   ├── dna/       # DNA file handling components
  │   ├── layout/    # Layout components
  │   ├── reports/   # Report viewing components
  │   └── shared/    # Shared UI components
  ├── contexts/      # React contexts for state management
  ├── hooks/         # Custom React hooks
  ├── pages/         # Page components
  ├── types/         # TypeScript type definitions
  ├── utils/         # Utility functions
  ├── App.tsx        # Main application component
  ├── config.ts      # Application configuration
  ├── index.tsx      # Entry point
  └── routes.tsx     # Application routes
```

### Making Changes

When making changes to the frontend, follow these guidelines:

1. **Component Modification**
   - React components are in the `components` directory, organized by feature
   - Page components that represent full routes are in the `pages` directory
   - Reuse existing components when possible

2. **API Integration**
   - API clients are in the `api` directory
   - Use the established patterns for making API calls
   - Handle loading states and errors appropriately

3. **State Management**
   - Use React Context for global state (auth, analysis data, etc.)
   - Use component state for UI-specific state
   - Context providers are in the `contexts` directory

4. **Routing**
   - Routes are defined in `routes.tsx`
   - Use React Router for navigation
   - Protected routes require authentication

### Adding New Components

To add a new component:

1. Create a new file in the appropriate directory under `components/`
2. Use TypeScript for type safety
3. Export the component as the default export
4. If needed, add to `index.ts` in the directory for barrel exports

Example:
```tsx
// src/components/shared/Button.tsx
import React from 'react';

interface ButtonProps {
  label: string;
  onClick: () => void;
  variant?: 'primary' | 'secondary';
}

const Button: React.FC<ButtonProps> = ({ 
  label, 
  onClick, 
  variant = 'primary' 
}) => {
  const baseClasses = "px-4 py-2 rounded font-medium";
  const variantClasses = variant === 'primary' 
    ? "bg-indigo-600 text-white hover:bg-indigo-700" 
    : "bg-gray-200 text-gray-800 hover:bg-gray-300";

  return (
    <button
      className={`${baseClasses} ${variantClasses}`}
      onClick={onClick}
    >
      {label}
    </button>
  );
};

export default Button;
```

### Implementing Authentication

The application uses JWT-based authentication. To work with authentication:

1. **User Login/Registration**
   - Components are in `components/auth/`
   - Authentication context is in `contexts/AuthContext.tsx`
   - API client is in `api/authApi.ts`

2. **Protected Routes**
   - Use the `ProtectedRoute` component to secure routes
   - This component automatically redirects to login if not authenticated

3. **Authentication State**
   - Use `useAuth()` hook to access authentication state and methods
   - Available properties: `user`, `isAuthenticated`, `isLoading`, `error`
   - Available methods: `login()`, `register()`, `logout()`, `updateProfile()`

4. **Google OAuth Integration**
   - To implement Google OAuth, follow the instructions in the `CLAUDE_EXPLANATION.md` file in the `google-auth-example` directory

### Styling Guidelines

The frontend uses Tailwind CSS for styling:

1. **Using Tailwind**
   - Use utility classes for most styling needs
   - Create custom components for repeated patterns
   - Refer to the [Tailwind documentation](https://tailwindcss.com/docs) for available classes

2. **Responsive Design**
   - Design for mobile-first
   - Use Tailwind's responsive prefixes (`sm:`, `md:`, `lg:`, etc.)
   - Test on multiple screen sizes

3. **Theme Consistency**
   - Use the color palette defined in `tailwind.config.js`
   - Maintain consistent spacing and typography
   - Follow established UI patterns for consistency

## Testing

### Frontend Testing

1. Run tests:
   ```bash
   cd frontend
   npm test
   ```

2. Run linting:
   ```bash
   npm run lint
   ```

3. Check TypeScript compilation:
   ```bash
   npm run typecheck
   ```

## Deployment

### Building for Production

To build the frontend for production:

```bash
cd frontend
npm run build
```

This creates a production-ready build in the `build` directory that can be deployed to a static hosting service.

### Docker Deployment

Use Docker Compose to run the complete application:

```bash
docker-compose up -d
```

This starts both the frontend and backend containers.

## Troubleshooting

### Common Issues

1. **API connection errors**
   - Check that the backend is running
   - Verify the `REACT_APP_API_URL` is correct in `.env`
   - Check browser console for CORS errors

2. **Authentication issues**
   - Clear browser localStorage
   - Verify the backend authentication service is working
   - Check token expiration settings

3. **Build errors**
   - Check for TypeScript type errors
   - Verify all dependencies are installed
   - Check for syntax errors in recent changes

### Getting Help

- Check the GitHub issues for known problems
- Review the API documentation for endpoint details
- Consult the project documentation for architecture information