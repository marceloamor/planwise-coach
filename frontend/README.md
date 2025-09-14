# PlanWise Coach Frontend

A modern Next.js frontend for the AI running coach application. Built with TypeScript, featuring a clean chat interface and beautiful plan visualization.

## ✨ Features

- **Chat Interface**: Natural conversation with AI running coach
- **Plan Display**: Beautiful, detailed training plan visualization
- **Anonymous Sessions**: No login required, uses device-based client IDs
- **Real-time Updates**: Plan updates instantly when AI generates new versions
- **Responsive Design**: Works seamlessly on desktop and mobile
- **TypeScript**: Fully typed for better development experience
- **Session Management**: Reset functionality to start fresh conversations

## 🚀 Quick Start

### Prerequisites

- Node.js 18+
- Backend running on `http://localhost:8000`

### Installation & Running

1. **Install dependencies:**
   ```bash
   cd frontend
   npm install
   ```

2. **Start development server:**
   ```bash
   npm run dev
   ```

3. **Open your browser:**
   Visit `http://localhost:3000`

## 📁 Project Structure

```
frontend/
├── app/
│   ├── page.tsx         # Main application page
│   ├── layout.tsx       # Root layout component
│   ├── globals.css      # Global styles
│   └── api.ts           # Backend API client
├── components/
│   ├── chat-panel.tsx   # Main chat interface
│   └── plan-card.tsx    # Training plan display
├── lib/
│   └── anon-id.ts       # Anonymous client ID management
├── package.json
├── tsconfig.json
├── next.config.js
└── README.md
```

## 🏗️ Architecture

### Tech Stack
- **Next.js 14**: App Router with modern React features
- **TypeScript**: Full type safety throughout
- **CSS Modules**: Component-scoped styling
- **React Hooks**: State management and effects
- **Fetch API**: HTTP client for backend communication

### Core Components

#### 1. Chat Panel (`components/chat-panel.tsx`)
The main interface component that handles:
- User message input and submission
- Chat history display
- Plan state management
- Session reset functionality
- API communication with backend

**Key Features:**
```typescript
// State management
const [clientId, setClientId] = useState<string>("");
const [messages, setMessages] = useState<ChatMessage[]>([]);
const [currentPlan, setCurrentPlan] = useState<PlanDoc | null>(null);
const [loading, setLoading] = useState(false);

// Real-time plan updates
if (response.plan_updated && response.plan) {
  setCurrentPlan(response.plan);
}
```

#### 2. Plan Card (`components/plan-card.tsx`)
Displays training plans with:
- Plan metadata (goal, phase, weekly targets)
- Weekly session breakdown
- Session details (type, distance, intensity, RPE)
- Responsive layout for different screen sizes

**Data Structure:**
```typescript
interface PlanCardProps {
  plan: PlanDoc;
  version?: number;
  updatedAt?: string;
}
```

#### 3. Anonymous ID Manager (`lib/anon-id.ts`)
Handles client identification:
- Generates unique UUIDs for new users
- Persists client IDs in localStorage
- Provides session reset functionality

```typescript
export function getAnonId(): string {
  // Returns existing ID or generates new one
}

export function resetAnonId(): string {
  // Generates fresh client ID for session reset
}
```

### API Layer (`app/api.ts`)

Type-safe API client with comprehensive error handling:

```typescript
// Main chat endpoint
export async function sendChat(clientId: string, message: string): Promise<ChatResponse>

// Plan retrieval
export async function fetchPlan(clientId: string): Promise<PlanResponse>

// Session reset
export async function resetSession(clientId: string): Promise<ResetResponse>

// Health check
export async function healthCheck(): Promise<HealthResponse>
```

## 🎨 Styling & Design

### Design System
- **Clean, minimal interface** focusing on readability
- **Consistent spacing** using CSS custom properties
- **Responsive typography** that scales across devices
- **Loading states** for better user experience
- **Error handling** with friendly messages

### Color Palette
```css
:root {
  --primary-color: #2563eb;
  --secondary-color: #64748b;
  --success-color: #059669;
  --error-color: #dc2626;
  --background: #ffffff;
  --text-primary: #1f2937;
  --text-secondary: #6b7280;
  --border: #e5e7eb;
}
```

### Component Styling
- **Scoped CSS** using CSS modules
- **Mobile-first** responsive design
- **Accessible** color contrasts and focus states
- **Smooth transitions** for interactive elements

## 🔧 Configuration

### Environment Variables
Create `.env.local` file:

```env
NEXT_PUBLIC_API_BASE=http://localhost:8000
```

### Next.js Configuration (`next.config.js`)
```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    // Future Next.js features
  }
}

module.exports = nextConfig
```

## 🧪 Development

### Type Safety
Full TypeScript integration with:
- **Interface definitions** for all API responses
- **Prop types** for all components
- **State type checking** with React hooks
- **API client types** matching backend schemas

### Error Handling
Comprehensive error management:
```typescript
try {
  const response = await sendChat(clientId, userMessage);
  // Handle success
} catch (err) {
  setError(err instanceof Error ? err.message : "Something went wrong");
  // Show error to user
}
```

### State Management
React hooks for local state:
- `useState` for component state
- `useEffect` for side effects
- `useRef` for DOM references
- Custom hooks for complex logic

### Performance Optimizations
- **Client-side routing** with Next.js
- **Automatic code splitting** for components
- **Optimized bundling** for production
- **Image optimization** (when images are added)

## 🚀 Production Deployment

### Build Process
```bash
npm run build    # Create production build
npm start        # Start production server
```

### Deployment Platforms
- **Vercel**: Seamless Next.js deployment
- **Netlify**: Static site hosting
- **Docker**: Containerized deployment
- **Traditional hosting**: Node.js compatible

### Environment Setup
```env
# Production environment variables
NEXT_PUBLIC_API_BASE=https://your-api-domain.com
NODE_ENV=production
```

## 🔄 Future Enhancements

### Planned Features
- **Plan History**: View previous plan versions
- **Export Functionality**: Download plans as PDF/calendar
- **Offline Support**: Service worker for offline access
- **Push Notifications**: Workout reminders
- **Social Features**: Share plans with coaches/friends

### Technical Improvements
- **State Management**: Consider Zustand/Redux for complex state
- **Caching**: React Query for server state management
- **Testing**: Add Jest + React Testing Library
- **Accessibility**: Enhanced ARIA labels and keyboard navigation
- **Performance**: Implement virtual scrolling for long plans

### UI/UX Enhancements
```typescript
// Enhanced plan visualization
interface EnhancedPlanCard {
  plan: PlanDoc;
  visualization: 'calendar' | 'timeline' | 'chart';
  interactive: boolean;
  exportOptions: ExportFormat[];
}

// Advanced session management
interface SessionManager {
  currentSessions: Session[];
  archiveSessions: (sessionIds: string[]) => void;
  exportSession: (sessionId: string, format: ExportFormat) => void;
  shareSession: (sessionId: string) => ShareLink;
}
```

## 🧪 Testing

### Test Structure
```bash
# Add comprehensive testing
npm install --save-dev jest @testing-library/react @testing-library/jest-dom

# Component tests
tests/
├── components/
│   ├── chat-panel.test.tsx
│   └── plan-card.test.tsx
├── lib/
│   └── anon-id.test.ts
└── api/
    └── api.test.ts
```

### Testing Best Practices
- **Component testing** with React Testing Library
- **API mocking** for reliable tests
- **Accessibility testing** with jest-axe
- **Visual regression** testing for UI consistency

## 🔍 Debugging

### Development Tools
- **React Developer Tools** browser extension
- **Next.js built-in debugging** with source maps
- **TypeScript compiler** for type checking
- **ESLint** for code quality

### Common Issues & Solutions

**Client ID Issues:**
- Check localStorage in browser dev tools
- Verify client ID format (UUID v4)
- Clear localStorage to reset

**API Connection:**
- Verify backend is running on correct port
- Check CORS configuration
- Monitor network tab for API calls

**Plan Display:**
- Validate plan structure matches TypeScript interfaces
- Check for null/undefined plan data
- Verify backend response format

## 💡 Development Guidelines

### Code Style
- **ESLint + Prettier** for consistent formatting
- **TypeScript strict mode** for type safety
- **Functional components** with hooks
- **Descriptive naming** for clarity

### Component Architecture
```typescript
// Component structure pattern
interface ComponentProps {
  // Define all props with types
}

export default function Component({ prop1, prop2 }: ComponentProps) {
  // State hooks
  const [state, setState] = useState<Type>(initialValue);
  
  // Effect hooks
  useEffect(() => {
    // Side effects
  }, [dependencies]);
  
  // Event handlers
  const handleEvent = useCallback(() => {
    // Handler logic
  }, [dependencies]);
  
  // Render
  return (
    <div>
      {/* JSX */}
    </div>
  );
}
```

### File Organization
- **Colocate related files** (component + styles + tests)
- **Barrel exports** for clean imports
- **Consistent naming** conventions
- **Clear folder structure** by feature

## 🤝 Contributing

### Getting Started
1. Fork the repository
2. Create a feature branch
3. Follow TypeScript and ESLint guidelines
4. Add tests for new features
5. Update documentation
6. Submit a pull request

### Code Review Checklist
- [ ] TypeScript types are accurate
- [ ] Components are accessible
- [ ] Error handling is implemented
- [ ] Performance implications considered
- [ ] Documentation is updated

The frontend is designed to be intuitive for users while maintaining clean, extensible code for developers. New features should integrate seamlessly with the existing chat-based interaction model. 