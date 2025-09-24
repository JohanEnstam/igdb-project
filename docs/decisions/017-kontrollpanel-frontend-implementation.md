# ADR-017: Kontrollpanel Frontend Implementation

**Datum:** 2025-01-27
**Status:** ✅ **ACCEPTED**
**Kontext:** Steg 2 av Web Application Development Plan

## 🎯 **Beslut**

Implementera en komplett Next.js kontrollpanel med Google Auth-integration för att skydda admin-funktioner och ge en central hub för systemövervakning.

## 📋 **Alternativ som Övervägdes**

### **Alternativ A: Token-baserad Autentisering**
- **Beskrivning**: Använd JWT tokens för frontend-backend kommunikation
- **Fördelar**: Stateless, skalbar
- **Nackdelar**: Komplex token-hantering, säkerhetsrisker med token storage
- **Status**: ❌ **AVVISAT**

### **Alternativ B: Session-baserad Autentisering** ⭐ **VALT**
- **Beskrivning**: Använd HTTP sessions med cookies för auth-state
- **Fördelar**: Enklare säkerhet, automatisk session-hantering
- **Nackdelar**: Server-side session storage
- **Status**: ✅ **ACCEPTERAT**

### **Alternativ C: Server-side Rendering (SSR)**
- **Beskrivning**: Rendera admin-sidor på servern med auth-check
- **Fördelar**: Bättre SEO, säkrare auth
- **Nackdelar**: Komplexare implementation, mindre interaktivitet
- **Status**: ❌ **AVVISAT**

## 🏗️ **Implementation Detaljer**

### **Frontend Arkitektur**
```tsx
// Admin Layout med Auth-skydd
export default function AdminLayout({ children }) {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState(null);

  // Google OAuth login
  const login = useGoogleLogin({
    onSuccess: async (tokenResponse) => {
      // Redirect till backend OAuth callback
      window.location.href = `/api/auth/callback?code=${tokenResponse.code}`;
    }
  });

  // Auth-check vid sidladdning
  useEffect(() => {
    checkAuth();
  }, []);
}
```

### **API Proxy Pattern**
```typescript
// Next.js API routes som proxy till backend
export async function GET(request: NextRequest) {
  const backendUrl = process.env.NEXT_PUBLIC_API_URL;
  const response = await fetch(`${backendUrl}/admin/status`, {
    headers: { "Cookie": request.headers.get("cookie") || "" },
    credentials: "include"
  });
  return NextResponse.json(await response.json());
}
```

### **Component Structure**
```
src/app/admin/
├── layout.tsx          # Auth-skyddad layout
├── page.tsx            # Dashboard med systemstatus
└── api/
    ├── admin/status/route.ts    # Proxy för backend admin endpoint
    ├── auth/callback/route.ts   # OAuth callback handler
    └── logout/route.ts          # Logout API proxy
```

## 🔧 **Tekniska Implementationer**

### **Dependencies Tillagda**
- `@react-oauth/google` - Google OAuth integration
- `axios` - HTTP client för API-anrop

### **OAuth Flow**
1. **Frontend**: Användare klickar "Sign in with Google"
2. **Google**: OAuth authorization code returneras
3. **Frontend**: Redirectar till `/api/auth/callback?code=...`
4. **Backend**: Exchangerar code för access token och skapar session
5. **Frontend**: Redirectar tillbaka till admin dashboard
6. **Session**: Alla efterföljande requests använder session cookies

### **Error Handling**
- **Auth Errors**: Visa tydliga felmeddelanden för OAuth-fel
- **API Errors**: Graceful fallback för backend-anrop
- **Network Errors**: Retry-logik för transienta fel
- **Loading States**: Spinner och skeleton loaders

## 🎨 **UI/UX Design**

### **Design System**
- **Tailwind CSS**: Utility-first CSS framework
- **Shadcn/ui**: Komponentbibliotek för konsistent design
- **Responsive Design**: Mobil-first approach
- **Accessibility**: WCAG 2.1 compliance

### **Dashboard Components**
- **Status Cards**: System health, game count, model status
- **User Info**: Användarprofil med avatar och namn
- **Quick Actions**: Buttons för vanliga admin-uppgifter
- **Error States**: Tydliga felmeddelanden och retry-options

## 🚨 **Lärdomar från Implementation**

### **1. OAuth Flow Complexity**
- **Problem**: Token-baserad auth var för komplex för session-baserad app
- **Lösning**: Använde session-baserad auth med cookies
- **Lärdom**: Välj auth-strategi baserat på app-typ (SPA vs traditionell web)

### **2. CORS och API Proxying**
- **Problem**: Frontend-backend CORS-konfiguration var komplex
- **Lösning**: Använde Next.js API routes som proxy
- **Lärdom**: API proxying förenklar CORS-hantering

### **3. Error State Management**
- **Problem**: Auth-fel var svåra att hantera gracefully
- **Lösning**: Implementerade comprehensive error handling
- **Lärdom**: Alltid planera för error states från början

### **4. Session Management**
- **Problem**: Session state var svår att synkronisera mellan frontend/backend
- **Lösning**: Använde cookies för automatisk session-hantering
- **Lärdom**: HTTP sessions är enklare än custom token-hantering

## 📊 **Success Metrics**

### **Funktionalitet**
- ✅ Admin-sida skyddad med Google Auth
- ✅ Dashboard visar spelantal och modell-status
- ✅ Responsiv design för mobil
- ✅ Error handling för auth-fel

### **Teknisk Kvalitet**
- ✅ Session-baserad autentisering
- ✅ API proxying för CORS-hantering
- ✅ Component separation of concerns
- ✅ TypeScript type safety

### **Användarupplevelse**
- ✅ Intuitiv login-flow
- ✅ Tydlig systemstatus
- ✅ Mobil-optimerad design
- ✅ Graceful error recovery

## 🔄 **Nästa Steg**

### **Steg 3: Monitoring Integration**
- Implementera GCP Monitoring API integration
- Lägg till pipeline triggers i dashboard
- Skapa belastningsgrafer med Chart.js

### **Steg 4: Skalbarhetstest**
- Testa systemet med 5,000+ spel
- Validera prestanda under belastning
- Dokumentera skalbarhetsbegränsningar

## 📚 **Referenser**

- **[WEB_APP_DEVELOPMENT_PLAN.md](../WEB_APP_DEVELOPMENT_PLAN.md)** - Komplett 4-stegs plan
- **[CURRENT_STATUS.md](../CURRENT_STATUS.md)** - Projektstatus och lärdomar
- **[ADR-016: Google Auth Implementation](016-google-auth-implementation.md)** - Backend auth implementation
- **[Next.js Documentation](https://nextjs.org/docs)** - Next.js best practices
- **[React OAuth Google](https://www.npmjs.com/package/@react-oauth/google)** - OAuth library documentation

---

**Beslut fattat**: 2025-01-27
**Implementerat**: 2025-01-27
**Nästa granskning**: 2025-01-30
**Status**: ✅ **COMPLETED**
