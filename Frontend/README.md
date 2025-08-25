
# Proposal Master Frontend

A React-based frontend for the Proposal Master AI-powered proposal management system.

## Features

- **Dashboard Overview**: System metrics and performance indicators
- **Document Management**: Upload, analyze, and search RFP documents
- **Proposal Management**: Create, track, and manage proposals
- **Research Tools**: Market research and competitive analysis
- **Real-time Integration**: Connected to FastAPI backend

## Quick Start

### Prerequisites

- Node.js 18+ and npm
- Backend API running on `http://localhost:8000`

### Installation

```bash
# Install dependencies
npm install

# Start development server
npm run dev
```

The application will be available at `http://localhost:5173`

### Backend Integration

The frontend connects to your Proposal Master API backend. Make sure to:

1. Start the backend API first:
   ```bash
   cd ..
   python dev_server.py
   ```

2. Update the API URL if needed in `.env`:
   ```
   VITE_API_URL=http://localhost:8000
   ```

## Components

### Main Sections

- **OverviewSection**: Dashboard with system metrics and charts
- **DocumentManagement**: File upload, search, and document analysis
- **ProposalManagement**: Proposal creation, tracking, and management
- **ResearchSection**: Market research and competitive intelligence

### API Integration

- **API Service** (`src/services/api.ts`): Handles all backend communication
- **React Hooks** (`src/hooks/useApi.ts`): State management for API data
- **Real-time Updates**: Automatic data refresh and synchronization

## Configuration

### Environment Variables

Create a `.env` file in the Frontend directory:

```
VITE_API_URL=http://localhost:8000
VITE_APP_TITLE=Proposal Master
VITE_UPLOAD_MAX_SIZE=52428800
```

### Backend Endpoints

The frontend expects these API endpoints:

- `GET /health` - System health check
- `GET /documents` - List documents
- `POST /documents/upload` - Upload documents
- `POST /vector/search` - Search documents
- `GET /proposals` - List proposals
- `POST /proposals` - Create proposals
- `POST /research/conduct` - Conduct research

## Development

### File Structure

```
src/
├── components/          # React components
│   ├── ui/             # Shared UI components
│   ├── DocumentManagement.tsx
│   ├── ProposalManagement.tsx
│   └── ...
├── services/           # API services
├── hooks/              # Custom React hooks
└── styles/            # CSS and styling
```

### Adding New Features

1. Create components in `src/components/`
2. Add API calls to `src/services/api.ts`
3. Create hooks in `src/hooks/useApi.ts`
4. Update navigation in `DashboardSidebar.tsx`

## Production Build

```bash
npm run build
```

This creates a `dist/` folder with production-ready files that can be served by any static file server.

## Backend Integration Notes

This frontend is specifically designed for the Proposal Master system with:

- FastAPI backend with CORS enabled
- Vector database for document search
- AI-powered document analysis
- Proposal generation and management
- Research capabilities

Make sure your backend has the corresponding API endpoints and CORS configuration for proper integration.
  