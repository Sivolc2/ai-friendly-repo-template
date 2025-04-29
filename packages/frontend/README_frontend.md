# Frontend

This directory contains the React/TypeScript frontend application.

## Technologies

- **React**: UI library
- **TypeScript**: Type safety
- **Vite**: Build tool and dev server
- **Tailwind CSS**: Utility-first CSS framework
- **React Router**: Client-side routing

## Directory Structure

```
├── public/         # Static assets
├── src/
│   ├── components/ # Reusable UI components
│   ├── hooks/      # Custom React hooks
│   ├── pages/      # Page components
│   ├── services/   # API clients and services
│   ├── types/      # TypeScript type definitions
│   ├── utils/      # Utility functions
│   ├── App.tsx     # Main application component
│   └── main.tsx    # Entry point
├── index.html      # HTML template
└── vite.config.ts  # Vite configuration
```

## Development

```bash
# Install dependencies
pnpm install

# Start development server
pnpm dev

# Build for production
pnpm build

# Preview production build
pnpm preview

# Run tests
pnpm test
```

## Component Development Guidelines

1. **Functional Components**: Use functional components with hooks
2. **TypeScript**: Add proper type definitions for all props and state
3. **Small Components**: Keep components small and focused on a single responsibility
4. **Composition**: Use composition over inheritance
5. **Testing**: Write tests for components
6. **Responsiveness**: Ensure components work well on all screen sizes

## Conventions

- File names: PascalCase for components, camelCase for utilities
- Component structure:
  - Props type definition
  - Component function
  - Export
- CSS: Use Tailwind utility classes

## Example Component

```tsx
import React from 'react';

type ButtonProps = {
  label: string;
  onClick: () => void;
  variant?: 'primary' | 'secondary' | 'outline';
  disabled?: boolean;
};

export const Button: React.FC<ButtonProps> = ({
  label,
  onClick,
  variant = 'primary',
  disabled = false,
}) => {
  const baseClasses = "px-4 py-2 rounded font-medium focus:outline-none";
  
  const variantClasses = {
    primary: "bg-blue-500 hover:bg-blue-600 text-white",
    secondary: "bg-gray-500 hover:bg-gray-600 text-white",
    outline: "border border-blue-500 text-blue-500 hover:bg-blue-50"
  };
  
  return (
    <button
      className={`${baseClasses} ${variantClasses[variant]} ${disabled ? 'opacity-50 cursor-not-allowed' : ''}`}
      onClick={onClick}
      disabled={disabled}
    >
      {label}
    </button>
  );
};
```

## Design Differences

- Components are organized by feature/domain rather than by type
- Services handle API communication and state management
- Shared types ensure consistency between frontend and backend 