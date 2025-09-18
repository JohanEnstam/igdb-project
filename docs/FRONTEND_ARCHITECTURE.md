# Frontend Architecture Documentation

## Overview

This document outlines the frontend architecture for the IGDB Game Recommendation System, including technical stack, component structure, performance considerations, and scalability strategy.

## Technical Stack

### Core Technologies
- **Next.js 14**: React framework with SSR, API routes, and built-in optimizations
- **TypeScript**: Type-safe JavaScript for better developer experience
- **Tailwind CSS**: Utility-first CSS framework for rapid styling
- **Shadcn/ui**: Copy-paste component library with Tailwind CSS
- **Lucide React**: Lightweight icon library with TypeScript support

### Development Tools
- **ESLint**: Code linting and quality enforcement
- **Prettier**: Code formatting
- **Husky**: Git hooks for quality gates
- **TypeScript**: Static type checking

## Project Structure

```
web_app/frontend/
├── app/                          # Next.js 14 App Router
│   ├── globals.css              # Global styles
│   ├── layout.tsx               # Root layout component
│   ├── page.tsx                 # Home page (search interface)
│   └── game/
│       └── [id]/
│           └── page.tsx         # Game details page
├── components/                   # Reusable components
│   ├── ui/                      # Shadcn/ui components
│   │   ├── input.tsx
│   │   ├── card.tsx
│   │   ├── button.tsx
│   │   └── ...
│   ├── GameSearch.tsx           # Main search component
│   ├── GameCard.tsx             # Game display card
│   ├── RecommendationList.tsx    # Recommendations display
│   ├── GameInfo.tsx             # Game information display
│   └── TextRecommendation.tsx   # Text-based recommendations
├── lib/                          # Utility functions
│   ├── api.ts                   # API client functions
│   ├── utils.ts                 # General utilities
│   └── types.ts                 # TypeScript type definitions
├── hooks/                        # Custom React hooks
│   ├── useGameSearch.ts         # Game search logic
│   ├── useRecommendations.ts    # Recommendations logic
│   └── useDebounce.ts           # Debouncing utility
├── styles/                       # Additional styles
│   └── components.css           # Component-specific styles
├── public/                       # Static assets
│   ├── images/
│   └── icons/
├── package.json
├── tailwind.config.js
├── tsconfig.json
└── next.config.js
```

## Component Architecture

### Core Components

#### GameSearch Component
```typescript
interface GameSearchProps {
  onGameSelect: (game: GameInfo) => void;
  placeholder?: string;
  className?: string;
}

// Features:
// - Autocomplete with debouncing (300ms)
// - Keyboard navigation
// - Loading states
// - Error handling
// - Accessibility (ARIA labels)
```

#### GameCard Component
```typescript
interface GameCardProps {
  game: GameInfo;
  onClick?: () => void;
  showRecommendations?: boolean;
  className?: string;
}

// Features:
// - Game information display
// - Rating visualization
// - Genre/platform tags
// - Hover effects
// - Responsive design
```

#### RecommendationList Component
```typescript
interface RecommendationListProps {
  gameId: number;
  topK?: number;
  className?: string;
}

// Features:
// - Similar games display
// - Similarity score visualization
// - Loading states
// - Error handling
// - Infinite scroll (future)
```

### UI Components (Shadcn/ui)

#### Input Component
- Autocomplete functionality
- Loading states
- Error states
- Accessibility features

#### Card Component
- Game information display
- Hover effects
- Responsive design
- Consistent styling

#### Button Component
- Various sizes and variants
- Loading states
- Disabled states
- Accessibility features

## API Integration

### API Client
```typescript
// lib/api.ts
class GameAPI {
  private baseURL: string;

  async searchGames(query: string, limit?: number): Promise<GameInfo[]>
  async getGameInfo(gameId: number): Promise<GameInfo>
  async getRecommendations(gameId: number, topK?: number): Promise<GameRecommendation[]>
  async getTextRecommendations(query: string, topK?: number): Promise<GameRecommendation[]>
  async getGenres(): Promise<string[]>
  async getPlatforms(): Promise<string[]>
}
```

### Type Definitions
```typescript
// lib/types.ts
interface GameInfo {
  id: number;
  name: string;
  summary: string;
  rating: number;
  rating_count: number;
  release_date: string;
  release_year: number;
  genre_names: string[];
  platform_names: string[];
  theme_names: string[];
}

interface GameRecommendation {
  game_id: number;
  name: string;
  similarity_score: number;
  rating?: number;
  genres?: string[];
  platforms?: string[];
  summary?: string;
}
```

## Performance Optimization

### Current Scale (1,230 games)
- **No optimization needed** - focus on UX
- **Debouncing**: 300ms for search input
- **Loading states**: Visual feedback for all async operations
- **Error handling**: Graceful error recovery

### Medium Scale (10,000 games)
- **Client-side filtering**: First 1000 games for autocomplete
- **Server-side search**: Exact matches for remaining games
- **Caching**: Popular searches cached for 5 minutes
- **Debouncing**: Increased to 500ms

### Large Scale (100,000+ games)
- **Search engine**: Elasticsearch integration
- **Vector database**: Recommendation engine overhaul
- **CDN**: Global content delivery
- **Edge functions**: Compute closer to users

## User Experience Flow

### Primary User Journey
```
1. User lands on homepage
   ↓
2. Sees prominent search field
   ↓
3. Types game name (autocomplete appears)
   ↓
4. Selects game from autocomplete
   ↓
5. Sees game info + recommendations
   ↓
6. Clicks recommendation → new game + new recommendations
```

### Secondary User Journey
```
1. User lands on homepage
   ↓
2. Types descriptive text ("space exploration game")
   ↓
3. Gets text-based recommendations
   ↓
4. Clicks recommendation → game details + similar games
```

## Responsive Design

### Breakpoints
- **Mobile**: 320px - 768px
- **Tablet**: 768px - 1024px
- **Desktop**: 1024px+

### Design Principles
- **Mobile-first**: Design for mobile, enhance for desktop
- **Touch-friendly**: Minimum 44px touch targets
- **Readable**: Minimum 16px font size
- **Accessible**: WCAG 2.1 AA compliance

## Accessibility

### WCAG 2.1 AA Compliance
- **Keyboard navigation**: All interactive elements accessible via keyboard
- **Screen readers**: Proper ARIA labels and semantic HTML
- **Color contrast**: Minimum 4.5:1 ratio for normal text
- **Focus management**: Clear focus indicators

### Implementation
- **Semantic HTML**: Proper heading hierarchy and landmarks
- **ARIA labels**: Descriptive labels for interactive elements
- **Alt text**: Descriptive alt text for images
- **Skip links**: Navigation skip links for screen readers

## State Management

### Local State (useState)
- **Search input**: Current search query
- **Selected game**: Currently selected game
- **Loading states**: Loading indicators for async operations
- **Error states**: Error messages and recovery

### Server State (React Query)
- **Game search**: Cached search results
- **Game info**: Cached game information
- **Recommendations**: Cached recommendation data
- **Metadata**: Cached genres and platforms

## Error Handling

### Error Types
- **Network errors**: API connectivity issues
- **Validation errors**: Invalid input data
- **Server errors**: Backend service issues
- **Not found errors**: Game not found

### Error Recovery
- **Retry mechanisms**: Automatic retry for transient errors
- **Fallback UI**: Graceful degradation
- **User feedback**: Clear error messages
- **Recovery actions**: Suggested next steps

## Testing Strategy

### Unit Tests
- **Component testing**: Individual component behavior
- **Hook testing**: Custom hook logic
- **Utility testing**: Helper function behavior

### Integration Tests
- **API integration**: End-to-end API calls
- **User flows**: Complete user journeys
- **Error scenarios**: Error handling behavior

### E2E Tests
- **Critical paths**: Main user journeys
- **Cross-browser**: Browser compatibility
- **Performance**: Load time and responsiveness

## Deployment

### Build Process
- **Next.js build**: Optimized production build
- **TypeScript compilation**: Type checking and compilation
- **CSS optimization**: Tailwind CSS purging
- **Asset optimization**: Image and static asset optimization

### Deployment Targets
- **GCP App Engine**: Primary deployment platform (Native Node.js runtime)
- **Configuration**: app.yaml-based deployment
- **CI/CD**: GitHub Actions with automated deployments
- **Scaling**: Automatic scaling (0-10 instances)

### Deployment Strategy (ADR-011)
- **Approach**: Native Node.js runtime instead of Docker containers
- **Benefits**: Simplified deployment, faster builds, higher reliability
- **Configuration**: Single app.yaml file vs complex Docker setup
- **Performance**: No container overhead, better resource utilization

## Monitoring

### Performance Metrics
- **Core Web Vitals**: LCP, FID, CLS
- **Page load time**: Initial page load performance
- **API latency**: Backend response times
- **Error rates**: Application error tracking

### User Experience Metrics
- **Search success rate**: Successful game searches
- **Recommendation clicks**: User engagement with recommendations
- **Bounce rate**: User retention metrics
- **Session duration**: User engagement time

## Future Enhancements

### Phase 2 Features
- **User accounts**: Personal recommendation history
- **Favorites**: Save favorite games
- **Advanced filters**: Genre, platform, rating filters
- **Social features**: Share recommendations

### Phase 3 Features
- **Machine learning**: Personalized recommendations
- **Real-time updates**: Live recommendation updates
- **Offline support**: PWA capabilities
- **Advanced analytics**: User behavior insights

## Conclusion

This frontend architecture provides a solid foundation for the IGDB Game Recommendation System, with clear scalability paths and modern development practices. The focus on user experience, performance, and accessibility ensures a high-quality application that can grow with our needs.
