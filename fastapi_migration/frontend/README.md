# Zando Genomic Analysis - React Frontend

This is the frontend application for the Zando Genomic Analysis platform. It provides a user-friendly interface for uploading DNA files, viewing analysis results, and generating personalized reports.

## Features

- DNA file upload with drag-and-drop support
- Real-time validation and processing feedback
- Interactive dashboard for viewing genetic analysis results
- Customizable report generation
- User authentication and data management

## Technical Overview

- Built with React 18 and TypeScript
- State management with React Context API
- Modern styling with Tailwind CSS
- Responsive design for all screen sizes
- API communication with Axios

## Getting Started

### Prerequisites

- Node.js 18+
- npm or yarn
- Backend API running (see backend README)

### Installation

1. Clone the repository
2. Install dependencies:
   ```
   npm install
   ```
3. Create a `.env` file with the following variables:
   ```
   REACT_APP_API_URL=http://localhost:8000/api/v1
   ```
4. Start the development server:
   ```
   npm start
   ```

## Project Structure

The project follows a feature-based organization:

```
/src
  /api                # API integration
  /components         # Reusable UI components
  /contexts           # React contexts for state
  /hooks              # Custom React hooks
  /pages              # Main application pages
  /types              # TypeScript declarations
  /utils              # Utility functions
  App.tsx             # Main application component
  index.tsx           # Application entry point
```

## API Integration

The frontend communicates with the FastAPI backend using the following endpoints:

- `/dna/upload` - Upload DNA files
- `/dna/validate` - Validate DNA files
- `/analysis/process` - Process DNA files for analysis
- `/reports/generate` - Generate personalized reports
- `/reports/{id}/download` - Download generated reports

## Development

### Running Tests

```
npm test
```

### Building for Production

```
npm run build
```

### Linting

```
npm run lint
```

## Component Library Overview

### Layout Components

- `Header` - Application header with navigation
- `Footer` - Application footer
- `Sidebar` - Navigation sidebar
- `Layout` - Main layout wrapper

### DNA Processing Components

- `FileUpload` - DNA file upload with drag and drop
- `FileValidator` - Validates uploaded DNA files
- `ProcessingStatus` - Shows processing status and progress

### Analysis Components

- `AnalysisResults` - Displays genetic analysis results
- `GeneticTraits` - Shows identified genetic traits
- `IngredientRecommendations` - Lists recommended skincare ingredients

### Report Components

- `ReportGenerator` - Interface for generating reports
- `ReportViewer` - PDF viewer for generated reports
- `ReportDownload` - Download controls for reports

## Authentication

The application supports user authentication with:

- User registration and login
- Secure storage of user preferences
- Session management

## State Management

Application state is managed through React Context:

- `AuthContext` - User authentication state
- `AnalysisContext` - Current analysis results
- `ReportContext` - Report generation state
- `NotificationContext` - System notifications

## Contributing

1. Fork the repository
2. Create a feature branch
3. Implement your changes
4. Add tests where appropriate
5. Submit a pull request

## License

This project is licensed under the MIT License.