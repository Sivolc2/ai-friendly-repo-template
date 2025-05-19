# Frontend Application

This directory contains a React + TypeScript frontend application for interacting with the backend API.

## Features

- View a list of items from the database
- Add new items to the database
- Delete items from the database

## Development

### Prerequisites

- Node.js (14.x or above)
- pnpm

### Setup

1. Install dependencies:
   ```bash
   pnpm install
   ```

2. Set up environment variables:
   ```bash
   cd ../../
   ./repo_src/scripts/setup-env.sh
   ```

### Running the development server

```bash
pnpm dev
```

This will start the development server on http://localhost:5173.

### Building for production

```bash
pnpm build
```

The built files will be placed in the `dist` directory.

## Project Structure

- `src/`: Source code
  - `components/`: Reusable React components
  - `styles/`: CSS files
  - `App.tsx`: Main application component
  - `main.tsx`: Application entry point

## Technologies Used

- React 18
- TypeScript
- Vite (build tool)
- CSS (for styling)

## API Integration

The frontend communicates with the backend API at `/api/items` for CRUD operations. The Vite development server is configured to proxy API requests to the backend server running on port 8000.
