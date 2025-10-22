# Technical Options Analysis
## Earnings Call Analyzer - Architecture and Technology Decisions

**Date:** October 22, 2025
**Purpose:** Evaluate technical options for implementing web-based user interface and enhanced features
**Scope:** Frontend frameworks, backend architecture, deployment models, database options

---

## Executive Summary

This document analyzes technical options for transforming the Earnings Call Analyzer from a CLI-only tool into an accessible web-based platform. After evaluating multiple approaches across 6 key decision areas, we recommend:

**🎯 RECOMMENDED ARCHITECTURE:**
- **Frontend:** React with TypeScript
- **Backend:** FastAPI (already planned)
- **Deployment:** Docker containers with optional cloud deployment
- **Database:** PostgreSQL (upgrade from SQLite)
- **Editor:** Monaco Editor for transcript editing
- **State Management:** React Context API (simple) or Zustand (if complex)

**Timeline:** 8-10 weeks for MVP
**Complexity:** Medium (manageable with existing Python expertise)

---

## Decision Matrix Summary

| Decision Area | Options Evaluated | Recommended Choice | Confidence |
|---------------|-------------------|-------------------|------------|
| Frontend Framework | React, Vue, Svelte, Vanilla | **React** | High |
| Backend Framework | FastAPI, Flask, Django | **FastAPI** (confirmed) | High |
| Database | SQLite, PostgreSQL, MySQL | **PostgreSQL** | Medium |
| Deployment Model | Local, Docker, Cloud, Hybrid | **Docker + Cloud** | High |
| Editor Component | Monaco, CodeMirror, ProseMirror | **Monaco** | High |
| Authentication | None, Basic, OAuth, JWT | **JWT** (future) | Medium |

---

## 1. Frontend Framework Selection

### Option A: React ⭐ RECOMMENDED

**Description:** Popular JavaScript library for building user interfaces, component-based architecture

**Pros:**
- ✅ **Largest ecosystem** - Most third-party components available
- ✅ **Strong TypeScript support** - Better type safety for large applications
- ✅ **Huge talent pool** - Easy to find developers
- ✅ **Monaco Editor** native React support (Microsoft's VS Code editor component)
- ✅ **Plotly.js** excellent React integration for data visualization
- ✅ **Mature tooling** - Create React App, Vite, Next.js options
- ✅ **Extensive documentation** and learning resources
- ✅ **Virtual DOM** for performance
- ✅ **React Hook Forms** for complex form handling (metadata entry)

**Cons:**
- ❌ Steeper learning curve than Vue
- ❌ More boilerplate code
- ❌ Bundle size can be larger
- ❌ Requires additional libraries for routing, state management

**Use Cases Best Suited:**
- Complex interactive dashboards
- Applications with many reusable components
- Long-term maintainability important
- Team may grow in future

**Technology Stack:**
```javascript
// Core
- React 18+ (with hooks)
- TypeScript
- Vite (build tool, faster than CRA)

// UI Components
- Material-UI (MUI) or Ant Design
- Monaco Editor (@monaco-editor/react)
- Plotly.js (react-plotly.js)

// State Management
- React Context API (simple state)
- Zustand or Jotai (if complex state needed)

// Forms & Validation
- React Hook Form
- Zod (TypeScript-first schema validation)

// Routing
- React Router v6

// HTTP Client
- Axios or native fetch
```

**Example Component Structure:**
```
frontend/
├── src/
│   ├── components/
│   │   ├── TranscriptEditor/
│   │   │   ├── MetadataForm.tsx
│   │   │   ├── TextEditor.tsx (Monaco)
│   │   │   ├── ValidationPreview.tsx
│   │   │   └── SpeakerManager.tsx
│   │   ├── Analysis/
│   │   │   ├── DashboardView.tsx
│   │   │   ├── SentimentChart.tsx
│   │   │   ├── DensityHeatmap.tsx
│   │   │   └── InformativenessGauge.tsx
│   │   └── Common/
│   │       ├── Button.tsx
│   │       └── LoadingSpinner.tsx
│   ├── pages/
│   │   ├── HomePage.tsx
│   │   ├── EditorPage.tsx
│   │   ├── AnalysisPage.tsx
│   │   └── ResultsPage.tsx
│   ├── hooks/
│   │   ├── useTranscriptValidation.ts
│   │   ├── useAnalysis.ts
│   │   └── useWebSocket.ts
│   ├── services/
│   │   └── api.ts
│   └── types/
│       └── transcript.ts
```

**Development Time:** 6-8 weeks for MVP
**Learning Curve:** Medium (1-2 weeks for Python developers new to React)

**Verdict:** ⭐⭐⭐⭐⭐ **Best choice for long-term scalability and ecosystem**

---

### Option B: Vue.js 3

**Description:** Progressive JavaScript framework, easier learning curve than React

**Pros:**
- ✅ **Easier to learn** - Simpler syntax, gentler learning curve
- ✅ **Official routing and state management** (Vue Router, Pinia)
- ✅ **Good documentation** - Very beginner-friendly
- ✅ **Smaller bundle size** than React
- ✅ **Composition API** similar to React Hooks
- ✅ **Single File Components** (HTML, CSS, JS in one file)
- ✅ **Good TypeScript support** (improving)

**Cons:**
- ❌ Smaller ecosystem than React
- ❌ Fewer component libraries
- ❌ Less corporate backing (compared to React/Facebook)
- ❌ Smaller talent pool
- ❌ Monaco Editor integration less mature

**Technology Stack:**
```javascript
- Vue 3 + Composition API
- TypeScript
- Vite
- Vue Router
- Pinia (state management)
- Element Plus or Vuetify (UI library)
```

**Development Time:** 5-7 weeks for MVP
**Learning Curve:** Low-Medium (easier entry than React)

**Verdict:** ⭐⭐⭐⭐ **Good alternative if team prefers simpler syntax**

---

### Option C: Svelte

**Description:** Compiler-based framework, writes code that surgically updates DOM

**Pros:**
- ✅ **Smallest bundle size** - Compiles to vanilla JS
- ✅ **Best performance** - No virtual DOM overhead
- ✅ **Simplest syntax** - Most intuitive for beginners
- ✅ **Built-in reactivity** - Less boilerplate
- ✅ **Built-in animations** - Smooth transitions out of box

**Cons:**
- ❌ **Smallest ecosystem** - Fewer ready-made components
- ❌ **Smallest community** - Harder to find help
- ❌ **Less mature** - Still evolving rapidly
- ❌ **Fewer jobs** - Harder to hire Svelte developers
- ❌ **Limited component libraries**

**Development Time:** 6-8 weeks (more custom work needed)
**Learning Curve:** Low

**Verdict:** ⭐⭐⭐ **Great for small teams, risky for scaling**

---

### Option D: Vanilla JavaScript + Web Components

**Description:** Pure JavaScript without frameworks

**Pros:**
- ✅ No framework lock-in
- ✅ Lightweight
- ✅ Fast load times

**Cons:**
- ❌ **Much more development time** - Reinventing the wheel
- ❌ No standard state management
- ❌ More boilerplate code
- ❌ Harder to maintain
- ❌ Poor developer experience

**Verdict:** ⭐ **Not recommended for complex applications**

---

## 2. Backend Framework (Confirmed)

### FastAPI ⭐ ALREADY SELECTED

**Rationale:** Already planned in Phase 2D, excellent choice

**Advantages for This Project:**
- ✅ **Async/await support** - Perfect for LLM calls (already using Ollama)
- ✅ **Automatic API documentation** - Swagger UI out of box
- ✅ **Type hints** - Pydantic models for validation
- ✅ **WebSocket support** - For real-time analysis updates
- ✅ **Fast performance** - Comparable to Node.js
- ✅ **Python ecosystem** - Leverage existing NLP/ML libraries
- ✅ **Easy integration** with existing codebase

**API Endpoint Structure:**
```python
# API routes to implement
POST /api/transcripts/upload          # Upload transcript file
POST /api/transcripts/validate        # Validate formatting
POST /api/transcripts/prepare         # Guided preparation
GET  /api/transcripts/{id}            # Get transcript
PUT  /api/transcripts/{id}            # Update transcript
DELETE /api/transcripts/{id}          # Delete transcript

POST /api/analysis/start              # Start analysis job
GET  /api/analysis/{job_id}/status    # Check analysis status
GET  /api/analysis/{job_id}/results   # Get results
WS   /api/analysis/{job_id}/stream    # WebSocket for real-time updates

GET  /api/speakers                    # Get speaker suggestions
POST /api/speakers/detect             # Auto-detect speakers

GET  /api/config                      # Get configuration
PUT  /api/config                      # Update configuration

GET  /api/reports/{id}/pdf            # Generate PDF report
GET  /api/reports/{id}/excel          # Generate Excel export
```

**Alternatives Considered:**

**Flask:**
- Simpler but lacks async support
- Would need extensions for everything
- Older, more mature
- **Verdict:** Too basic for our needs

**Django:**
- Batteries included (ORM, admin, auth)
- Heavier framework
- Overkill for API-only backend
- **Verdict:** Too heavyweight

---

## 3. Database Selection

### Current State: SQLite (Phase 2B)

**SQLite Limitations:**
- ❌ Single-user (file-based locking)
- ❌ No concurrent writes
- ❌ Limited scalability
- ❌ No user management
- ✅ Good for development
- ✅ Zero configuration

---

### Option A: PostgreSQL ⭐ RECOMMENDED

**Description:** Powerful open-source relational database

**Pros:**
- ✅ **JSONB support** - Store analysis results as JSON with indexing
- ✅ **Concurrent connections** - Multiple users
- ✅ **Full-text search** - Search transcripts
- ✅ **Transactions** - ACID compliance
- ✅ **Scalability** - Handles millions of records
- ✅ **Advanced analytics** - Window functions, CTEs
- ✅ **Free and open-source**
- ✅ **Strong Python support** - SQLAlchemy, psycopg3
- ✅ **Cloud-ready** - AWS RDS, Google Cloud SQL, etc.

**Cons:**
- ❌ Requires setup (vs SQLite's zero-config)
- ❌ More resource intensive
- ❌ Need to manage backups

**Schema Enhancements:**
```sql
-- Users table (for multi-user support)
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255),
    full_name VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE
);

-- Enhanced transcripts table
CREATE TABLE transcripts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    company_id INTEGER REFERENCES companies(id),
    raw_text TEXT,
    formatted_text TEXT,
    metadata JSONB,  -- Store as JSONB for querying
    speaker_mappings JSONB,
    section_boundaries JSONB,
    status VARCHAR(50),  -- draft, validated, analyzed
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Index for JSON querying
CREATE INDEX idx_transcript_metadata ON transcripts USING GIN (metadata);

-- Enhanced analysis results
CREATE TABLE analysis_results (
    id SERIAL PRIMARY KEY,
    transcript_id INTEGER REFERENCES transcripts(id),
    analysis_type VARCHAR(50),  -- full, deception_only, etc.
    results JSONB,  -- Full analysis results
    sentence_density JSONB,  -- NEW: Sentence-level metrics
    distribution_patterns JSONB,  -- NEW
    informativeness_metrics JSONB,  -- NEW
    created_at TIMESTAMP DEFAULT NOW(),
    computation_time_seconds FLOAT
);

-- Analysis jobs queue
CREATE TABLE analysis_jobs (
    id SERIAL PRIMARY KEY,
    transcript_id INTEGER REFERENCES transcripts(id),
    user_id INTEGER REFERENCES users(id),
    status VARCHAR(50),  -- queued, running, completed, failed
    progress INTEGER,  -- 0-100
    error_message TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    started_at TIMESTAMP,
    completed_at TIMESTAMP
);
```

**Migration Path:**
```bash
# 1. Export SQLite data
python scripts/export_sqlite_data.py

# 2. Setup PostgreSQL
docker run -d --name postgres \
  -e POSTGRES_PASSWORD=secret \
  -e POSTGRES_DB=earnings_analyzer \
  -p 5432:5432 postgres:15

# 3. Run Alembic migrations
alembic upgrade head

# 4. Import data
python scripts/import_to_postgres.py
```

**Verdict:** ⭐⭐⭐⭐⭐ **Best for production deployment**

---

### Option B: MySQL

**Pros:**
- ✅ Widely used
- ✅ Good performance
- ✅ Cloud providers support

**Cons:**
- ❌ Weaker JSON support than PostgreSQL
- ❌ Less advanced features
- ❌ Oracle ownership concerns

**Verdict:** ⭐⭐⭐ **PostgreSQL is better for JSON-heavy workload**

---

### Option C: MongoDB

**Pros:**
- ✅ Native JSON/document storage
- ✅ Flexible schema
- ✅ Horizontal scaling

**Cons:**
- ❌ No transactions (in older versions)
- ❌ Lose relational benefits
- ❌ Overkill for this use case
- ❌ Learning curve if team knows SQL

**Verdict:** ⭐⭐ **Not recommended - PostgreSQL JSONB gives best of both worlds**

---

## 4. Deployment Model

### Option A: Docker Containers ⭐ RECOMMENDED

**Description:** Containerize frontend, backend, database, and Ollama

**Architecture:**
```yaml
# docker-compose.yml
version: '3.8'

services:
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend
    environment:
      - REACT_APP_API_URL=http://localhost:8000

  backend:
    build: .
    ports:
      - "8000:8000"
    depends_on:
      - postgres
      - ollama
    volumes:
      - ./data:/app/data
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/earnings_analyzer
      - OLLAMA_HOST=http://ollama:11434

  postgres:
    image: postgres:15
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      - POSTGRES_PASSWORD=secret
      - POSTGRES_DB=earnings_analyzer

  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    # GPU support (optional)
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]

volumes:
  postgres_data:
  ollama_data:
```

**Pros:**
- ✅ **Consistent environments** - Dev = Staging = Production
- ✅ **Easy deployment** - Single `docker-compose up`
- ✅ **Isolation** - Services don't conflict
- ✅ **Scalability** - Can deploy to Kubernetes later
- ✅ **Version control** - Dockerfile tracks dependencies
- ✅ **Portability** - Runs anywhere Docker runs

**Cons:**
- ❌ Requires Docker knowledge
- ❌ Larger disk usage
- ❌ Slight performance overhead (minimal)

**Deployment Commands:**
```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f backend

# Run database migrations
docker-compose exec backend alembic upgrade head

# Pull Ollama model
docker-compose exec ollama ollama pull llama3.1:8b

# Stop all services
docker-compose down
```

**Cloud Deployment Options:**

**AWS:**
```bash
# Option 1: ECS (Elastic Container Service)
- Push images to ECR
- Create ECS task definitions
- Deploy to Fargate (serverless) or EC2
- Cost: ~$50-150/month for small workload

# Option 2: EC2 + Docker Compose
- Launch t3.large instance (GPU: g4dn.xlarge for Ollama)
- Install Docker
- Run docker-compose
- Cost: ~$70/month (t3.large) or ~$500/month (g4dn)
```

**Google Cloud:**
```bash
# Cloud Run (easiest)
gcloud run deploy earnings-analyzer \
  --source . \
  --region us-central1

# Cost: Pay per request, ~$20-100/month
```

**DigitalOcean:**
```bash
# App Platform
- Connect GitHub repo
- Auto-deploy on push
- Cost: ~$12-25/month for basic app
```

**Verdict:** ⭐⭐⭐⭐⭐ **Best balance of simplicity and scalability**

---

### Option B: Traditional VM Deployment

**Description:** Install everything on a Linux server

**Pros:**
- ✅ Lower overhead
- ✅ Direct hardware access
- ✅ Familiar to sysadmins

**Cons:**
- ❌ "Works on my machine" problems
- ❌ Harder to scale
- ❌ Manual dependency management
- ❌ Harder to reproduce environments

**Verdict:** ⭐⭐ **Docker is better**

---

### Option C: Kubernetes

**Description:** Container orchestration platform

**Pros:**
- ✅ Excellent scalability
- ✅ Auto-healing
- ✅ Load balancing

**Cons:**
- ❌ **Massive overkill** for current scale
- ❌ Steep learning curve
- ❌ Complex to manage
- ❌ High operational overhead

**Verdict:** ⭐ **Save for future if you reach 1000+ users**

---

### Option D: Serverless

**Description:** AWS Lambda, Google Cloud Functions, etc.

**Pros:**
- ✅ Auto-scaling
- ✅ Pay per use
- ✅ No server management

**Cons:**
- ❌ **Cold start latency** - Bad for LLM calls
- ❌ **Timeout limits** - 15 min max (AWS), transcripts may take longer
- ❌ **Ollama won't work** - Can't run custom models
- ❌ Complex state management

**Verdict:** ⭐ **Not suitable for LLM-heavy workload**

---

## 5. Text Editor Component

### Option A: Monaco Editor ⭐ RECOMMENDED

**Description:** VS Code's editor, used by GitHub, StackBlitz

**Pros:**
- ✅ **Best-in-class** - Same editor as VS Code
- ✅ **Syntax highlighting** - Can highlight speaker names, sections
- ✅ **IntelliSense** - Auto-complete for speaker names
- ✅ **Diff viewer** - Compare versions
- ✅ **Find/replace** - Built-in
- ✅ **Line numbers** - Easier navigation
- ✅ **Minimap** - Overview of document
- ✅ **Undo/redo** - Full history
- ✅ **Themes** - VS Code themes work
- ✅ **Accessibility** - Screen reader support

**Cons:**
- ❌ Large bundle (~2.5MB gzipped)
- ❌ Requires Web Workers

**React Integration:**
```typescript
import Editor from '@monaco-editor/react';

function TranscriptEditor({ value, onChange }) {
  return (
    <Editor
      height="600px"
      defaultLanguage="plaintext"
      theme="vs-dark"
      value={value}
      onChange={onChange}
      options={{
        minimap: { enabled: true },
        lineNumbers: 'on',
        folding: true,
        wordWrap: 'on',
        automaticLayout: true,
      }}
    />
  );
}
```

**Custom Language Support:**
```typescript
// Define custom highlighting for transcript format
monaco.languages.register({ id: 'earnings-transcript' });

monaco.languages.setMonarchTokensProvider('earnings-transcript', {
  tokenizer: {
    root: [
      [/^Company:/, 'keyword'],
      [/^Ticker:/, 'keyword'],
      [/^Quarter:/, 'keyword'],
      [/^\s*[A-Z][a-z]+ [A-Z][a-z]+ - [A-Za-z\s]+:/, 'type'], // Speaker
      [/PREPARED REMARKS/, 'string'],
      [/QUESTIONS AND ANSWERS/, 'string'],
    ]
  }
});
```

**Verdict:** ⭐⭐⭐⭐⭐ **Industry standard, best features**

---

### Option B: CodeMirror 6

**Description:** Lightweight code editor

**Pros:**
- ✅ Smaller bundle (~500KB)
- ✅ Good performance
- ✅ Modular architecture
- ✅ Mobile-friendly

**Cons:**
- ❌ Less features than Monaco
- ❌ Smaller ecosystem
- ❌ More configuration needed

**Verdict:** ⭐⭐⭐⭐ **Good if bundle size is critical**

---

### Option C: ProseMirror

**Description:** Rich text editor framework (like Google Docs)

**Pros:**
- ✅ WYSIWYG editing
- ✅ Collaborative editing possible
- ✅ Flexible schema

**Cons:**
- ❌ Overkill for plain text
- ❌ Steeper learning curve
- ❌ More complex setup

**Verdict:** ⭐⭐ **Not needed for transcript editing**

---

### Option D: Simple Textarea

**Description:** Basic HTML textarea

**Pros:**
- ✅ Zero dependencies
- ✅ Fast load
- ✅ Simple

**Cons:**
- ❌ No syntax highlighting
- ❌ No line numbers
- ❌ Poor UX for large files
- ❌ No auto-complete

**Verdict:** ⭐ **Too basic for good user experience**

---

## 6. Authentication & User Management

### Option A: JWT (JSON Web Tokens) ⭐ RECOMMENDED (Future)

**Description:** Stateless token-based authentication

**Pros:**
- ✅ **Stateless** - No session storage needed
- ✅ **Scalable** - Works across multiple servers
- ✅ **Standard** - Widely supported
- ✅ **FastAPI-native** - `python-jose` library
- ✅ **Mobile-ready** - Works with mobile apps

**Cons:**
- ❌ Token revocation requires extra work
- ❌ Larger payload than session cookies

**Implementation:**
```python
# backend/api/auth.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta

SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        return email
    except JWTError:
        raise credentials_exception
```

**Verdict:** ⭐⭐⭐⭐⭐ **Industry standard for APIs**

---

### Option B: No Authentication (MVP)

**Description:** No user accounts, anyone can use

**Pros:**
- ✅ Fastest to implement
- ✅ No friction for users
- ✅ Good for MVP/demo

**Cons:**
- ❌ No user data separation
- ❌ No usage tracking
- ❌ Can't save user preferences
- ❌ Not production-ready

**Verdict:** ⭐⭐⭐ **OK for initial MVP, add auth later**

---

### Option C: OAuth 2.0 (Google, GitHub)

**Description:** "Sign in with Google" style

**Pros:**
- ✅ No password management
- ✅ Users trust Google/GitHub
- ✅ Easy onboarding

**Cons:**
- ❌ Depends on third party
- ❌ More complex setup
- ❌ Privacy concerns for some users

**Verdict:** ⭐⭐⭐⭐ **Good addition after JWT is working**

---

## 7. Real-Time Updates Strategy

### WebSocket vs Server-Sent Events vs Polling

**Challenge:** Analysis takes 1-3 minutes, users need progress updates

---

### Option A: WebSockets ⭐ RECOMMENDED

**Description:** Bi-directional real-time communication

**Pros:**
- ✅ **Real-time updates** - Instant progress notifications
- ✅ **Bi-directional** - Can cancel jobs
- ✅ **FastAPI support** - Built-in WebSocket support
- ✅ **Efficient** - Persistent connection

**Implementation:**
```python
# backend/api/websocket.py
from fastapi import WebSocket

@app.websocket("/ws/analysis/{job_id}")
async def analysis_websocket(websocket: WebSocket, job_id: str):
    await websocket.accept()

    try:
        while True:
            # Get job status
            job = await get_analysis_job(job_id)

            # Send progress update
            await websocket.send_json({
                "status": job.status,
                "progress": job.progress,
                "current_step": job.current_step,
                "eta_seconds": job.eta
            })

            if job.status in ["completed", "failed"]:
                break

            await asyncio.sleep(1)  # Update every second

    except WebSocketDisconnect:
        print(f"Client disconnected from job {job_id}")
```

**Frontend:**
```typescript
// React hook for WebSocket
function useAnalysisProgress(jobId: string) {
  const [progress, setProgress] = useState(0);
  const [status, setStatus] = useState('queued');

  useEffect(() => {
    const ws = new WebSocket(`ws://localhost:8000/ws/analysis/${jobId}`);

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setProgress(data.progress);
      setStatus(data.status);
    };

    return () => ws.close();
  }, [jobId]);

  return { progress, status };
}
```

**Verdict:** ⭐⭐⭐⭐⭐ **Best for real-time features**

---

### Option B: Server-Sent Events (SSE)

**Pros:**
- ✅ Simpler than WebSocket
- ✅ Auto-reconnect
- ✅ HTTP-based

**Cons:**
- ❌ One-way only (server → client)
- ❌ Can't cancel jobs easily

**Verdict:** ⭐⭐⭐ **Good if you don't need bi-directional**

---

### Option C: Polling

**Description:** Frontend repeatedly checks status

**Pros:**
- ✅ Simplest implementation
- ✅ Works everywhere

**Cons:**
- ❌ Inefficient (many unnecessary requests)
- ❌ Delayed updates (polling interval)
- ❌ Higher server load

**Verdict:** ⭐⭐ **Fallback option only**

---

## 8. File Upload Strategy

### Option A: Direct Upload to Server ⭐ RECOMMENDED (MVP)

**Description:** Upload files directly to FastAPI backend

**Pros:**
- ✅ Simple implementation
- ✅ No third-party dependencies
- ✅ Full control

**Cons:**
- ❌ Server storage usage
- ❌ Doesn't scale to huge files

**Implementation:**
```python
# backend/api/upload.py
from fastapi import UploadFile, File

@app.post("/api/transcripts/upload")
async def upload_transcript(
    file: UploadFile = File(...),
    company_name: str = Form(...),
    ticker: str = Form(...),
    quarter: str = Form(...),
    year: int = Form(...)
):
    # Validate file type
    if not file.filename.endswith(('.txt', '.md', '.pdf', '.docx')):
        raise HTTPException(400, "Invalid file type")

    # Check file size (max 10MB)
    contents = await file.read()
    if len(contents) > 10 * 1024 * 1024:
        raise HTTPException(400, "File too large")

    # Save file
    file_path = f"data/uploads/{file.filename}"
    with open(file_path, 'wb') as f:
        f.write(contents)

    # Create transcript record
    transcript = await create_transcript(
        file_path=file_path,
        company_name=company_name,
        ticker=ticker,
        quarter=quarter,
        year=year
    )

    return {"transcript_id": transcript.id}
```

**Verdict:** ⭐⭐⭐⭐⭐ **Perfect for MVP**

---

### Option B: Cloud Storage (S3, Google Cloud Storage)

**Pros:**
- ✅ Unlimited storage
- ✅ CDN integration
- ✅ Durability/redundancy

**Cons:**
- ❌ Costs money
- ❌ More complex
- ❌ External dependency

**Verdict:** ⭐⭐⭐ **Add later if needed**

---

## 9. Frontend Build & Bundling

### Option A: Vite ⭐ RECOMMENDED

**Description:** Next-generation build tool

**Pros:**
- ✅ **Extremely fast** - 10-100x faster than Webpack
- ✅ **Hot Module Replacement** - Instant updates
- ✅ **ES modules native** - Modern approach
- ✅ **Smaller bundle sizes**
- ✅ **TypeScript support** built-in
- ✅ **Simple configuration**

**Setup:**
```bash
npm create vite@latest earnings-analyzer-frontend -- --template react-ts
cd earnings-analyzer-frontend
npm install
npm run dev  # Development server
npm run build  # Production build
```

**Verdict:** ⭐⭐⭐⭐⭐ **Industry standard for new React projects**

---

### Option B: Create React App

**Pros:**
- ✅ Official React tool
- ✅ Zero configuration
- ✅ Well documented

**Cons:**
- ❌ **Slower** than Vite
- ❌ Larger bundles
- ❌ Being phased out by React team

**Verdict:** ⭐⭐ **Vite is better**

---

## 10. Recommended Tech Stack Summary

### MVP Stack (8-10 weeks):

```
┌─────────────────────────────────────────────────┐
│              USER BROWSER                       │
│  ┌───────────────────────────────────────────┐ │
│  │   React 18 + TypeScript + Vite            │ │
│  │   - Material-UI components                │ │
│  │   - Monaco Editor                         │ │
│  │   - Plotly.js charts                      │ │
│  │   - React Router                          │ │
│  │   - Axios for HTTP                        │ │
│  └───────────────────────────────────────────┘ │
└─────────────────────────────────────────────────┘
                       │
                       │ HTTP / WebSocket
                       ▼
┌─────────────────────────────────────────────────┐
│          BACKEND (FastAPI + Python)             │
│  ┌───────────────────────────────────────────┐ │
│  │   API Routes (REST + WebSocket)           │ │
│  │   - Transcript CRUD                       │ │
│  │   - Analysis endpoints                    │ │
│  │   - File upload                           │ │
│  │   - Real-time updates                     │ │
│  └───────────────────────────────────────────┘ │
│  ┌───────────────────────────────────────────┐ │
│  │   Business Logic                          │ │
│  │   - Existing analyzers (sentiment, etc.)  │ │
│  │   - NEW: Sentence density analyzer        │ │
│  │   - NEW: Informativeness metrics          │ │
│  └───────────────────────────────────────────┘ │
└─────────────────────────────────────────────────┘
         │                        │
         │                        │
         ▼                        ▼
┌──────────────────┐    ┌──────────────────┐
│   PostgreSQL     │    │   Ollama LLM     │
│   - Transcripts  │    │   - llama3.1:8b  │
│   - Results      │    │   - API on       │
│   - Users (fut.) │    │     :11434       │
│   - Jobs queue   │    │                  │
└──────────────────┘    └──────────────────┘
```

### Technology Decisions:

| Component | Choice | Alternative | Rationale |
|-----------|--------|-------------|-----------|
| **Frontend Framework** | React 18 + TypeScript | Vue 3, Svelte | Largest ecosystem, best tooling |
| **UI Library** | Material-UI (MUI) | Ant Design | Clean design, comprehensive |
| **Text Editor** | Monaco Editor | CodeMirror | VS Code quality, best features |
| **Build Tool** | Vite | Webpack, CRA | 10x faster, modern |
| **Backend Framework** | FastAPI | Flask, Django | Already planned, async support |
| **Database** | PostgreSQL | SQLite, MongoDB | JSONB support, scalability |
| **Deployment** | Docker Compose | K8s, VMs | Simple, portable, scalable |
| **Cloud (optional)** | AWS ECS | GCP, DO | Most mature, flexible |
| **Authentication** | JWT (future) | OAuth, None | Standard for APIs |
| **Real-time** | WebSockets | SSE, Polling | Bi-directional, efficient |
| **State Management** | React Context | Redux, Zustand | Simple, built-in |

---

## 11. Implementation Roadmap

### Phase 1: Foundation (Weeks 1-2)

**Backend:**
- [ ] Set up FastAPI project structure
- [ ] Implement basic CRUD endpoints for transcripts
- [ ] Set up PostgreSQL with Docker
- [ ] Create database migrations (Alembic)
- [ ] Implement file upload endpoint

**Frontend:**
- [ ] Initialize Vite + React + TypeScript project
- [ ] Set up routing (React Router)
- [ ] Create basic layout and navigation
- [ ] Implement API client (Axios)
- [ ] Set up Material-UI theme

**DevOps:**
- [ ] Create Dockerfile for backend
- [ ] Create Dockerfile for frontend
- [ ] Set up docker-compose.yml
- [ ] Configure environment variables

---

### Phase 2: Editor Implementation (Weeks 3-4)

**Frontend:**
- [ ] Integrate Monaco Editor
- [ ] Build metadata form component
- [ ] Implement speaker detection preview
- [ ] Add section highlighting
- [ ] Create validation feedback UI
- [ ] Implement auto-save (localStorage initially)

**Backend:**
- [ ] POST /api/transcripts/validate endpoint
- [ ] POST /api/transcripts/prepare endpoint
- [ ] GET /api/speakers/detect endpoint
- [ ] Integrate with existing TranscriptProcessor

---

### Phase 3: Analysis Integration (Weeks 5-6)

**Frontend:**
- [ ] Build analysis dashboard (Plotly charts)
- [ ] Implement sentence density heatmap visualization
- [ ] Create informativeness gauge
- [ ] Add progress bar for long-running analyses

**Backend:**
- [ ] POST /api/analysis/start endpoint
- [ ] Implement job queue (in-memory initially)
- [ ] WebSocket endpoint for progress updates
- [ ] Integrate new sentence density analyzer
- [ ] Integrate informativeness metrics

**Database:**
- [ ] Extend schema for sentence-level metrics
- [ ] Add analysis_jobs table
- [ ] Implement job status tracking

---

### Phase 4: Polish & Testing (Weeks 7-8)

**Frontend:**
- [ ] Error handling and user feedback
- [ ] Loading states and skeletons
- [ ] Responsive design (mobile-friendly)
- [ ] Accessibility improvements
- [ ] PDF/Excel export buttons

**Backend:**
- [ ] Error handling middleware
- [ ] Input validation (Pydantic)
- [ ] Rate limiting
- [ ] Logging improvements
- [ ] API documentation (Swagger)

**Testing:**
- [ ] Frontend: Jest + React Testing Library
- [ ] Backend: Pytest
- [ ] E2E: Playwright or Cypress
- [ ] Load testing: Locust

**Documentation:**
- [ ] User guide
- [ ] API documentation
- [ ] Deployment guide
- [ ] Architecture documentation

---

## 12. Cost Estimate

### Development Costs (Time):

| Phase | Developer Time | Cost (@$100/hr) |
|-------|----------------|-----------------|
| Phase 1: Foundation | 80 hours | $8,000 |
| Phase 2: Editor | 80 hours | $8,000 |
| Phase 3: Analysis | 80 hours | $8,000 |
| Phase 4: Polish | 80 hours | $8,000 |
| **Total** | **320 hours (8 weeks)** | **$32,000** |

---

### Infrastructure Costs (Monthly):

**Self-Hosted (Recommended for MVP):**
- DigitalOcean Droplet (4GB RAM, 2 vCPU): **$24/month**
- Storage (100GB): **$10/month**
- Backups: **$5/month**
- **Total: ~$40/month**

**Cloud-Hosted (AWS):**
- ECS Fargate (2 vCPU, 4GB RAM): **$60/month**
- RDS PostgreSQL (db.t3.small): **$30/month**
- EC2 for Ollama (t3.large): **$70/month**
- ALB (Load Balancer): **$20/month**
- S3 Storage: **$5/month**
- **Total: ~$185/month**

**Cloud-Hosted with GPU (for faster LLM):**
- GPU instance (g4dn.xlarge): **$500/month**
- Other services: **$100/month**
- **Total: ~$600/month**

---

## 13. Risk Assessment

### Technical Risks:

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| **Ollama LLM performance issues** | Medium | High | Implement caching, queue system, optional --no-llm mode |
| **Large file uploads timeout** | Medium | Medium | Implement chunked upload, increase timeout limits |
| **WebSocket connection drops** | Medium | Low | Auto-reconnect logic, fallback to polling |
| **Database migration issues** | Low | High | Thorough testing, backup before migration |
| **Bundle size too large** | Low | Medium | Code splitting, lazy loading, use Vite |
| **Concurrent user scaling** | Medium | Medium | Connection pooling, caching, load testing |

### Non-Technical Risks:

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| **Scope creep** | High | High | Strict MVP definition, phased approach |
| **User adoption slow** | Medium | Medium | User testing, documentation, tutorials |
| **Hosting costs exceed budget** | Low | Medium | Start with cheapest option, monitor usage |
| **Complexity overwhelms users** | Medium | High | Extensive UX testing, wizard-style flows |

---

## 14. Success Metrics

### Technical Metrics:
- **Page load time:** < 2 seconds
- **Analysis completion time:** < 3 minutes for 5,000-word transcript
- **Uptime:** > 99% (planned downtime excluded)
- **Error rate:** < 1% of requests
- **Bundle size:** < 1MB (gzipped)

### User Metrics:
- **Onboarding time:** < 5 minutes from signup to first analysis
- **User satisfaction:** > 4.0/5.0 (if surveyed)
- **Analysis success rate:** > 95% (transcripts that complete without errors)
- **Return usage:** > 50% of users run multiple analyses

---

## 15. Decision Summary & Recommendations

### ✅ RECOMMENDED DECISIONS:

1. **Frontend:** React 18 + TypeScript + Vite
2. **Backend:** FastAPI (confirmed)
3. **Database:** PostgreSQL (upgrade from SQLite)
4. **Editor:** Monaco Editor
5. **Deployment:** Docker Compose (local/cloud-agnostic)
6. **Authentication:** None for MVP, JWT in Phase 2
7. **Real-time:** WebSockets for progress updates
8. **Hosting:** Start with DigitalOcean ($40/month), scale to AWS if needed

### 🎯 ARCHITECTURE DIAGRAM:

```
User (Browser)
  ↓
React App (Vite build)
  ↓ HTTP REST API
FastAPI Backend
  ↓ SQL           ↓ HTTP
PostgreSQL      Ollama
```

### 📅 TIMELINE:

- **Weeks 1-2:** Foundation (FastAPI + React setup, Docker)
- **Weeks 3-4:** Editor (Monaco integration, metadata forms)
- **Weeks 5-6:** Analysis (integrate new sentence-level features)
- **Weeks 7-8:** Polish (testing, docs, deployment)

**Total: 8 weeks to MVP**

### 💰 BUDGET:

- **Development:** $32,000 (320 hours @ $100/hr) or 8 weeks full-time
- **Infrastructure:** $40-185/month depending on hosting choice

---

## 16. Alternative Minimal Approach

If 8 weeks is too long, consider this **4-week ultra-minimal approach**:

### Tech Stack:
- **Frontend:** Plain HTML + Vanilla JavaScript + Bootstrap
- **Backend:** FastAPI (existing)
- **Database:** Keep SQLite
- **Editor:** Simple <textarea> with syntax guide
- **Deployment:** Single Heroku dyno or DigitalOcean droplet
- **No authentication**

**Pros:**
- ✅ 50% faster development
- ✅ Lower complexity
- ✅ Easier to maintain

**Cons:**
- ❌ Much worse UX
- ❌ Limited scalability
- ❌ Technical debt

**Verdict:** Only if time is critical constraint

---

## Conclusion

The recommended architecture strikes the optimal balance between:
- **User Experience:** Professional, accessible web interface
- **Development Speed:** 8 weeks to MVP with proven technologies
- **Scalability:** Can grow from 10 to 10,000 users without rewrite
- **Maintainability:** Standard stack, easy to hire developers
- **Cost:** Reasonable $40-185/month infrastructure costs

**Next Steps:**
1. Review and approve recommended stack
2. Set up development environment
3. Begin Phase 1 (Foundation) implementation
4. Iterate based on user feedback

---

**Document Version:** 1.0
**Last Updated:** October 22, 2025
**Author:** Claude Code
**Status:** Ready for stakeholder review
