# Phase 2D Roadmap: API & Web Interface

**Version:** 2.0.0-phase2d  
**Date:** October 17, 2025  
**Status:** Planning & Design  
**Priority:** MEDIUM  
**Estimated Duration:** 2-3 weeks

---

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Architecture Design](#architecture-design)
4. [Implementation Plan](#implementation-plan)
5. [API Endpoints Specification](#api-endpoints-specification)
6. [Data Models](#data-models)
7. [Web Interface Design](#web-interface-design)
8. [Testing Strategy](#testing-strategy)
9. [Deployment Considerations](#deployment-considerations)
10. [Success Criteria](#success-criteria)
11. [Timeline & Milestones](#timeline--milestones)

---

## Overview

### Phase 2D Goals

Phase 2D transforms the Earnings Call Analyzer into a web-accessible platform by adding:

1. **RESTful API** - Programmatic access to all analysis capabilities
2. **Job Queue System** - Background processing for long-running analyses
3. **Web Interface** - User-friendly dashboard for non-technical users
4. **Multi-format Output** - Results available in JSON, PDF, HTML, Excel
5. **Real-time Status** - Live job tracking and progress updates

### What Phase 2D Enables

- **Remote Access**: Analyze transcripts from any device via web browser
- **Batch Processing**: Queue multiple analyses without blocking
- **Team Collaboration**: Share results via URLs
- **API Integration**: Integrate with existing business intelligence tools
- **Scalability**: Handle concurrent requests from multiple users

### Phase Context

```
Phase 2C: Advanced Reporting        ✅ COMPLETE
    ↓
Phase 2D: API & Web Interface       🔄 CURRENT PHASE
    ↓
Phase 2E: Advanced Analytics        📋 PLANNED
```

---

## Prerequisites

### Completed Phases Required

✅ **Phase 1**: Core analysis modules (sentiment, complexity, numerical)  
✅ **Phase 2A**: Deception detection and evasiveness analysis  
✅ **Phase 2B**: Database and persistence layer  
✅ **Phase 2C**: Advanced reporting (PDF, HTML, Excel)

### System Requirements

- Python 3.8+
- SQLite database (from Phase 2B)
- All Phase 2C reporting dependencies
- Additional Phase 2D dependencies (see below)

### New Dependencies

```txt
# Core API Framework
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
python-multipart>=0.0.6
pydantic>=2.4.0

# Job Queue (Optional but Recommended)
redis>=5.0.0
rq>=1.15.0

# Additional API Tools
python-jose[cryptography]>=3.3.0  # Optional: JWT authentication
passlib[bcrypt]>=1.7.4            # Optional: Password hashing
aiofiles>=23.2.1                  # Async file operations

# Testing
pytest-asyncio>=0.21.0
httpx>=0.25.0
```

---

## Architecture Design

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Web Browser / API Client                │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                      FastAPI Application                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Routes     │  │  Middleware  │  │    Auth      │     │
│  │  (Endpoints) │  │   (CORS)     │  │  (Optional)  │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                      Job Queue Layer                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  Job Queue   │  │   Workers    │  │    Status    │     │
│  │   (Redis)    │  │   (RQ/bg)    │  │   Tracking   │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   Business Logic Layer                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  Aggregator  │  │  Deception   │  │  Reporting   │     │
│  │  (Phase 1)   │  │  (Phase 2A)  │  │  (Phase 2C)  │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    Data Persistence Layer                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Database   │  │  File Store  │  │   Cache      │     │
│  │  (Phase 2B)  │  │   (Uploads)  │  │  (Optional)  │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

### Directory Structure

```
src/
├── api/
│   ├── __init__.py
│   ├── app.py                  # FastAPI application
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── analysis.py         # Analysis endpoints
│   │   ├── jobs.py             # Job management endpoints
│   │   ├── results.py          # Results retrieval endpoints
│   │   ├── historical.py       # Historical data endpoints
│   │   ├── comparison.py       # Peer comparison endpoints
│   │   └── health.py           # Health check endpoints
│   ├── models/
│   │   ├── __init__.py
│   │   ├── requests.py         # Pydantic request models
│   │   ├── responses.py        # Pydantic response models
│   │   └── jobs.py             # Job status models
│   ├── services/
│   │   ├── __init__.py
│   │   ├── analysis_service.py # Core analysis orchestration
│   │   ├── job_service.py      # Job queue management
│   │   └── file_service.py     # File upload handling
│   ├── middleware/
│   │   ├── __init__.py
│   │   ├── cors.py             # CORS configuration
│   │   └── error_handler.py    # Error handling
│   └── dependencies.py         # FastAPI dependencies
│
├── web/
│   ├── static/
│   │   ├── css/
│   │   │   └── styles.css
│   │   ├── js/
│   │   │   ├── main.js
│   │   │   ├── upload.js
│   │   │   └── results.js
│   │   └── images/
│   └── templates/
│       ├── index.html          # Main dashboard
│       ├── upload.html         # Upload interface
│       ├── results.html        # Results display
│       └── history.html        # Historical view
│
└── jobs/
    ├── __init__.py
    ├── worker.py               # Job worker
    ├── tasks.py                # Background tasks
    └── queue.py                # Queue configuration
```

---

## Implementation Plan

### Phase 2D.1: Core API Framework (Week 1, Days 1-3)

**Objective**: Set up FastAPI application with basic structure

#### Tasks

1. **Create API Application** (`src/api/app.py`)
   - Initialize FastAPI app
   - Configure CORS middleware
   - Add exception handlers
   - Set up logging
   - Configure static file serving

2. **Create Pydantic Models** (`src/api/models/`)
   - Request models for analysis submission
   - Response models for results
   - Job status models
   - Error response models

3. **Create Health Check Endpoint** (`src/api/routes/health.py`)
   - Basic health check: `GET /health`
   - Detailed health check: `GET /health/detailed`
   - Check database connectivity
   - Check dependencies availability

4. **Set Up Dependencies** (`src/api/dependencies.py`)
   - Database session dependency
   - Repository dependency injection
   - Configuration dependency

#### Files to Create

```python
# src/api/app.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from src.api.routes import health, analysis, jobs, results
from src.api.middleware.error_handler import add_exception_handlers

app = FastAPI(
    title="Earnings Call Analyzer API",
    description="Advanced earnings call transcript analysis with deception detection",
    version="2.0.0-phase2d"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="src/web/static"), name="static")

# Include routers
app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(analysis.router, prefix="/api/analyze", tags=["analysis"])
app.include_router(jobs.router, prefix="/api/jobs", tags=["jobs"])
app.include_router(results.router, prefix="/api/results", tags=["results"])

# Add exception handlers
add_exception_handlers(app)

@app.get("/")
async def root():
    return {
        "message": "Earnings Call Analyzer API",
        "version": "2.0.0-phase2d",
        "docs": "/docs",
        "health": "/health"
    }
```

```python
# src/api/models/requests.py
from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum

class OutputFormat(str, Enum):
    JSON = "json"
    PDF = "pdf"
    HTML = "html"
    EXCEL = "excel"

class AnalysisRequest(BaseModel):
    company_name: str = Field(..., min_length=1, max_length=255)
    ticker: str = Field(..., min_length=1, max_length=10)
    quarter: str = Field(..., pattern=r"Q[1-4]")
    year: int = Field(..., ge=2000, le=2100)
    output_formats: List[OutputFormat] = Field(default=[OutputFormat.JSON])
    enable_deception: bool = Field(default=True)
    
    class Config:
        json_schema_extra = {
            "example": {
                "company_name": "Apple Inc.",
                "ticker": "AAPL",
                "quarter": "Q4",
                "year": 2024,
                "output_formats": ["json", "pdf"],
                "enable_deception": True
            }
        }

class FileUploadMetadata(BaseModel):
    filename: str
    content_type: str
    size: int
```

```python
# src/api/models/responses.py
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum

class JobStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class JobResponse(BaseModel):
    job_id: str
    status: JobStatus
    created_at: datetime
    updated_at: datetime
    progress: Optional[int] = Field(None, ge=0, le=100)
    message: Optional[str] = None
    
class AnalysisResultResponse(BaseModel):
    job_id: str
    company_name: str
    ticker: str
    quarter: str
    year: int
    analysis_data: Dict[str, Any]
    generated_files: List[str] = Field(default_factory=list)
    completed_at: datetime

class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
    status_code: int
```

#### Acceptance Criteria

- ✅ FastAPI app starts successfully: `uvicorn src.api.app:app --reload`
- ✅ Health check endpoint returns 200: `GET /health`
- ✅ API documentation available at `/docs`
- ✅ CORS configured correctly
- ✅ All Pydantic models validate correctly

---

### Phase 2D.2: File Upload & Analysis Endpoints (Week 1, Days 4-5)

**Objective**: Implement transcript upload and analysis submission

#### Tasks

1. **File Upload Service** (`src/api/services/file_service.py`)
   - Handle multipart file uploads
   - Validate file types (txt, pdf)
   - Extract text from uploads
   - Store files temporarily
   - Generate unique file IDs

2. **Analysis Service** (`src/api/services/analysis_service.py`)
   - Integrate with Phase 1 aggregator
   - Integrate with Phase 2A deception modules
   - Integrate with Phase 2B database
   - Integrate with Phase 2C reporting
   - Handle analysis orchestration

3. **Analysis Endpoints** (`src/api/routes/analysis.py`)
   - `POST /api/analyze/upload` - Upload file and start analysis
   - `POST /api/analyze/text` - Submit text directly
   - `GET /api/analyze/supported-formats` - List supported formats

#### Files to Create

```python
# src/api/services/file_service.py
import uuid
import shutil
from pathlib import Path
from fastapi import UploadFile
from typing import Tuple

class FileService:
    def __init__(self, upload_dir: str = "data/uploads"):
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)
    
    async def save_upload(self, file: UploadFile) -> Tuple[str, Path]:
        """Save uploaded file and return (file_id, file_path)"""
        file_id = str(uuid.uuid4())
        file_extension = Path(file.filename).suffix
        file_path = self.upload_dir / f"{file_id}{file_extension}"
        
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        return file_id, file_path
    
    def read_transcript(self, file_path: Path) -> str:
        """Read transcript text from file"""
        if file_path.suffix == '.txt':
            return file_path.read_text(encoding='utf-8')
        elif file_path.suffix == '.pdf':
            # TODO: Add PDF text extraction
            raise NotImplementedError("PDF extraction not yet implemented")
        else:
            raise ValueError(f"Unsupported file type: {file_path.suffix}")
    
    def cleanup_file(self, file_path: Path):
        """Delete uploaded file"""
        if file_path.exists():
            file_path.unlink()
```

```python
# src/api/services/analysis_service.py
from src.analysis.aggregator import AnalysisAggregator
from src.database.repository import DatabaseRepository
from src.reporting.pdf_generator import PDFReportGenerator
from src.reporting.html_dashboard import HTMLDashboardGenerator
from src.reporting.excel_exporter import ExcelReportExporter
from typing import Dict, Any, List
from pathlib import Path

class AnalysisService:
    def __init__(self, db_repository: DatabaseRepository):
        self.repository = db_repository
        self.aggregator = AnalysisAggregator()
        self.pdf_gen = PDFReportGenerator()
        self.html_gen = HTMLDashboardGenerator()
        self.excel_exp = ExcelReportExporter()
    
    def analyze_transcript(
        self,
        transcript_text: str,
        company_name: str,
        ticker: str,
        quarter: str,
        year: int,
        output_formats: List[str]
    ) -> Dict[str, Any]:
        """
        Run complete analysis pipeline
        Returns: {
            'analysis_data': {...},
            'generated_files': [...]
        }
        """
        # Run analysis
        analysis_data = self.aggregator.analyze(
            transcript_text,
            company_name,
            ticker,
            quarter,
            year
        )
        
        # Save to database
        result_id = self.repository.save_analysis_result(
            company_name=company_name,
            ticker=ticker,
            quarter=quarter,
            year=year,
            transcript_text=transcript_text,
            analysis_data=analysis_data
        )
        
        # Generate reports
        generated_files = []
        output_dir = Path(f"data/outputs/{ticker}_{quarter}_{year}")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        if 'pdf' in output_formats:
            pdf_path = self.pdf_gen.generate_report(
                analysis_data,
                str(output_dir / f"{ticker}_{quarter}_{year}_report.pdf")
            )
            generated_files.append(str(pdf_path))
        
        if 'html' in output_formats:
            html_path = self.html_gen.generate_dashboard(
                analysis_data,
                str(output_dir / f"{ticker}_{quarter}_{year}_dashboard.html")
            )
            generated_files.append(str(html_path))
        
        if 'excel' in output_formats:
            excel_path = self.excel_exp.export_to_excel(
                analysis_data,
                str(output_dir / f"{ticker}_{quarter}_{year}_workbook.xlsx")
            )
            generated_files.append(str(excel_path))
        
        return {
            'result_id': result_id,
            'analysis_data': analysis_data,
            'generated_files': generated_files
        }
```

```python
# src/api/routes/analysis.py
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from src.api.models.requests import AnalysisRequest, OutputFormat
from src.api.models.responses import JobResponse, JobStatus
from src.api.services.file_service import FileService
from src.api.services.job_service import JobService
from datetime import datetime
import uuid

router = APIRouter()

@router.post("/upload", response_model=JobResponse)
async def analyze_upload(
    file: UploadFile = File(...),
    company_name: str = ...,
    ticker: str = ...,
    quarter: str = ...,
    year: int = ...,
    output_formats: str = "json",  # Comma-separated
    enable_deception: bool = True,
    file_service: FileService = Depends(),
    job_service: JobService = Depends()
):
    """Upload transcript file and start analysis"""
    
    # Validate file type
    if not file.filename.endswith(('.txt', '.pdf')):
        raise HTTPException(400, "Only .txt and .pdf files supported")
    
    # Save file
    file_id, file_path = await file_service.save_upload(file)
    
    # Create job
    job_id = str(uuid.uuid4())
    formats = [f.strip() for f in output_formats.split(',')]
    
    # Queue analysis job
    job = await job_service.create_job(
        job_id=job_id,
        file_path=str(file_path),
        company_name=company_name,
        ticker=ticker,
        quarter=quarter,
        year=year,
        output_formats=formats,
        enable_deception=enable_deception
    )
    
    return JobResponse(
        job_id=job_id,
        status=JobStatus.PENDING,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        message="Analysis job queued successfully"
    )

@router.post("/text", response_model=JobResponse)
async def analyze_text(
    request: AnalysisRequest,
    transcript_text: str,
    job_service: JobService = Depends()
):
    """Submit transcript text directly for analysis"""
    
    job_id = str(uuid.uuid4())
    
    # Queue analysis job
    job = await job_service.create_job(
        job_id=job_id,
        transcript_text=transcript_text,
        company_name=request.company_name,
        ticker=request.ticker,
        quarter=request.quarter,
        year=request.year,
        output_formats=[f.value for f in request.output_formats],
        enable_deception=request.enable_deception
    )
    
    return JobResponse(
        job_id=job_id,
        status=JobStatus.PENDING,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        message="Analysis job queued successfully"
    )

@router.get("/supported-formats")
async def get_supported_formats():
    """List supported input and output formats"""
    return {
        "input_formats": [".txt", ".pdf"],
        "output_formats": ["json", "pdf", "html", "excel"]
    }
```

#### Acceptance Criteria

- ✅ File upload endpoint accepts .txt files
- ✅ Analysis job created successfully
- ✅ Job ID returned in response
- ✅ Files stored in upload directory
- ✅ Text extraction works for .txt files

---

### Phase 2D.3: Job Queue System (Week 1, Days 6-7)

**Objective**: Implement background job processing

#### Tasks

1. **Job Service** (`src/api/services/job_service.py`)
   - Job creation and tracking
   - Status updates
   - Progress tracking
   - Error handling

2. **Job Queue** (`src/jobs/queue.py`)
   - Redis connection (optional)
   - In-memory queue (fallback)
   - Job persistence
   - Queue management

3. **Worker** (`src/jobs/worker.py`)
   - Background worker process
   - Job execution
   - Error recovery
   - Cleanup

4. **Tasks** (`src/jobs/tasks.py`)
   - Analysis task
   - Reporting task
   - Cleanup task

#### Files to Create

```python
# src/jobs/queue.py
from typing import Dict, Any, Optional
import json
from datetime import datetime
from pathlib import Path

class JobQueue:
    """Simple in-memory job queue (can be upgraded to Redis)"""
    
    def __init__(self):
        self.jobs: Dict[str, Dict[str, Any]] = {}
        self.jobs_dir = Path("data/jobs")
        self.jobs_dir.mkdir(parents=True, exist_ok=True)
    
    def enqueue(self, job_id: str, job_data: Dict[str, Any]):
        """Add job to queue"""
        job_data['status'] = 'pending'
        job_data['created_at'] = datetime.now().isoformat()
        job_data['updated_at'] = datetime.now().isoformat()
        
        self.jobs[job_id] = job_data
        
        # Persist to disk
        job_file = self.jobs_dir / f"{job_id}.json"
        job_file.write_text(json.dumps(job_data, indent=2))
    
    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get job by ID"""
        if job_id in self.jobs:
            return self.jobs[job_id]
        
        # Try loading from disk
        job_file = self.jobs_dir / f"{job_id}.json"
        if job_file.exists():
            job_data = json.loads(job_file.read_text())
            self.jobs[job_id] = job_data
            return job_data
        
        return None
    
    def update_status(self, job_id: str, status: str, message: str = None, progress: int = None):
        """Update job status"""
        if job_id not in self.jobs:
            return False
        
        self.jobs[job_id]['status'] = status
        self.jobs[job_id]['updated_at'] = datetime.now().isoformat()
        
        if message:
            self.jobs[job_id]['message'] = message
        if progress is not None:
            self.jobs[job_id]['progress'] = progress
        
        # Persist to disk
        job_file = self.jobs_dir / f"{job_id}.json"
        job_file.write_text(json.dumps(self.jobs[job_id], indent=2))
        
        return True
    
    def get_pending_jobs(self):
        """Get all pending jobs"""
        return [
            (job_id, job_data)
            for job_id, job_data in self.jobs.items()
            if job_data.get('status') == 'pending'
        ]
```

```python
# src/jobs/tasks.py
from src.api.services.analysis_service import AnalysisService
from src.api.services.file_service import FileService
from src.database.repository import DatabaseRepository
from src.jobs.queue import JobQueue
from config.settings import settings
from pathlib import Path
import traceback

def run_analysis_task(job_id: str, job_queue: JobQueue):
    """Execute analysis task"""
    
    # Get job data
    job_data = job_queue.get_job(job_id)
    if not job_data:
        return
    
    try:
        # Update status
        job_queue.update_status(job_id, 'processing', 'Starting analysis...', 0)
        
        # Initialize services
        repository = DatabaseRepository(settings.DATABASE_URL)
        analysis_service = AnalysisService(repository)
        file_service = FileService()
        
        # Get transcript text
        if 'file_path' in job_data:
            job_queue.update_status(job_id, 'processing', 'Reading transcript...', 10)
            transcript_text = file_service.read_transcript(Path(job_data['file_path']))
        else:
            transcript_text = job_data['transcript_text']
        
        # Run analysis
        job_queue.update_status(job_id, 'processing', 'Running analysis...', 30)
        result = analysis_service.analyze_transcript(
            transcript_text=transcript_text,
            company_name=job_data['company_name'],
            ticker=job_data['ticker'],
            quarter=job_data['quarter'],
            year=job_data['year'],
            output_formats=job_data['output_formats']
        )
        
        # Update job with results
        job_data['result_id'] = result['result_id']
        job_data['generated_files'] = result['generated_files']
        
        # Cleanup
        if 'file_path' in job_data:
            file_service.cleanup_file(Path(job_data['file_path']))
        
        # Mark complete
        job_queue.update_status(
            job_id, 
            'completed', 
            'Analysis completed successfully',
            100
        )
        
    except Exception as e:
        error_msg = f"Analysis failed: {str(e)}"
        job_queue.update_status(job_id, 'failed', error_msg)
        print(f"Job {job_id} failed:")
        traceback.print_exc()
```

```python
# src/jobs/worker.py
import time
from src.jobs.queue import JobQueue
from src.jobs.tasks import run_analysis_task
import signal
import sys

class Worker:
    def __init__(self, queue: JobQueue, poll_interval: int = 5):
        self.queue = queue
        self.poll_interval = poll_interval
        self.running = True
        
        # Handle graceful shutdown
        signal.signal(signal.SIGINT, self.shutdown)
        signal.signal(signal.SIGTERM, self.shutdown)
    
    def shutdown(self, signum, frame):
        """Graceful shutdown"""
        print("\nShutting down worker...")
        self.running = False
    
    def run(self):
        """Main worker loop"""
        print("Worker started. Polling for jobs...")
        
        while self.running:
            # Get pending jobs
            pending = self.queue.get_pending_jobs()
            
            for job_id, job_data in pending:
                print(f"Processing job: {job_id}")
                run_analysis_task(job_id, self.queue)
            
            # Sleep
            time.sleep(self.poll_interval)
        
        print("Worker stopped.")

if __name__ == "__main__":
    queue = JobQueue()
    worker = Worker(queue)
    worker.run()
```

```python
# src/api/services/job_service.py
from src.jobs.queue import JobQueue
from typing import Dict, Any, Optional, List

class JobService:
    def __init__(self):
        self.queue = JobQueue()
    
    async def create_job(
        self,
        job_id: str,
        company_name: str,
        ticker: str,
        quarter: str,
        year: int,
        output_formats: List[str],
        enable_deception: bool,
        file_path: Optional[str] = None,
        transcript_text: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create and enqueue a new job"""
        
        job_data = {
            'company_name': company_name,
            'ticker': ticker,
            'quarter': quarter,
            'year': year,
            'output_formats': output_formats,
            'enable_deception': enable_deception
        }
        
        if file_path:
            job_data['file_path'] = file_path
        if transcript_text:
            job_data['transcript_text'] = transcript_text
        
        self.queue.enqueue(job_id, job_data)
        return job_data
    
    async def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get current job status"""
        return self.queue.get_job(job_id)
    
    async def get_all_jobs(self) -> List[Dict[str, Any]]:
        """Get all jobs"""
        return [
            {'job_id': job_id, **job_data}
            for job_id, job_data in self.queue.jobs.items()
        ]
```

#### Acceptance Criteria

- ✅ Jobs enqueue successfully
- ✅ Worker processes jobs from queue
- ✅ Job status updates correctly
- ✅ Progress tracking works
- ✅ Error handling works
- ✅ Worker can be stopped gracefully

---

### Phase 2D.4: Results & Job Management Endpoints (Week 2, Days 1-2)

**Objective**: Implement endpoints for retrieving results and managing jobs

#### Tasks

1. **Job Management Endpoints** (`src/api/routes/jobs.py`)
   - `GET /api/jobs/{job_id}` - Get job status
   - `GET /api/jobs` - List all jobs
   - `DELETE /api/jobs/{job_id}` - Cancel/delete job

2. **Results Endpoints** (`src/api/routes/results.py`)
   - `GET /api/results/{job_id}` - Get analysis results (JSON)
   - `GET /api/results/{job_id}/download` - Download report file
   - `GET /api/results/{job_id}/files` - List generated files

#### Files to Create

```python
# src/api/routes/jobs.py
from fastapi import APIRouter, HTTPException, Depends
from src.api.models.responses import JobResponse, JobStatus
from src.api.services.job_service import JobService
from typing import List
from datetime import datetime

router = APIRouter()

@router.get("/{job_id}", response_model=JobResponse)
async def get_job_status(
    job_id: str,
    job_service: JobService = Depends()
):
    """Get status of a specific job"""
    
    job_data = await job_service.get_job_status(job_id)
    
    if not job_data:
        raise HTTPException(404, f"Job {job_id} not found")
    
    return JobResponse(
        job_id=job_id,
        status=JobStatus(job_data['status']),
        created_at=datetime.fromisoformat(job_data['created_at']),
        updated_at=datetime.fromisoformat(job_data['updated_at']),
        progress=job_data.get('progress'),
        message=job_data.get('message')
    )

@router.get("", response_model=List[JobResponse])
async def list_jobs(
    status: str = None,
    job_service: JobService = Depends()
):
    """List all jobs, optionally filtered by status"""
    
    all_jobs = await job_service.get_all_jobs()
    
    if status:
        all_jobs = [j for j in all_jobs if j['status'] == status]
    
    return [
        JobResponse(
            job_id=job['job_id'],
            status=JobStatus(job['status']),
            created_at=datetime.fromisoformat(job['created_at']),
            updated_at=datetime.fromisoformat(job['updated_at']),
            progress=job.get('progress'),
            message=job.get('message')
        )
        for job in all_jobs
    ]

@router.delete("/{job_id}")
async def delete_job(
    job_id: str,
    job_service: JobService = Depends()
):
    """Delete a job and its associated files"""
    
    # TODO: Implement job deletion
    return {"message": f"Job {job_id} deleted"}
```

```python
# src/api/routes/results.py
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse
from src.api.services.job_service import JobService
from src.database.repository import DatabaseRepository
from config.settings import settings
from pathlib import Path
from typing import List

router = APIRouter()

@router.get("/{job_id}")
async def get_results(
    job_id: str,
    job_service: JobService = Depends()
):
    """Get analysis results as JSON"""
    
    job_data = await job_service.get_job_status(job_id)
    
    if not job_data:
        raise HTTPException(404, f"Job {job_id} not found")
    
    if job_data['status'] != 'completed':
        raise HTTPException(400, f"Job {job_id} is not completed yet")
    
    # Get result from database
    repository = DatabaseRepository(settings.DATABASE_URL)
    result = repository.get_analysis_by_id(job_data['result_id'])
    
    if not result:
        raise HTTPException(404, "Analysis results not found")
    
    return {
        'job_id': job_id,
        'company_name': result.company_name,
        'ticker': result.ticker,
        'quarter': result.quarter,
        'year': result.year,
        'analysis_data': result.analysis_data,
        'generated_files': job_data.get('generated_files', []),
        'completed_at': job_data['updated_at']
    }

@router.get("/{job_id}/files")
async def list_result_files(
    job_id: str,
    job_service: JobService = Depends()
):
    """List all generated files for a job"""
    
    job_data = await job_service.get_job_status(job_id)
    
    if not job_data:
        raise HTTPException(404, f"Job {job_id} not found")
    
    files = job_data.get('generated_files', [])
    
    return {
        'job_id': job_id,
        'files': [
            {
                'filename': Path(f).name,
                'path': f,
                'type': Path(f).suffix,
                'size': Path(f).stat().st_size if Path(f).exists() else 0
            }
            for f in files
        ]
    }

@router.get("/{job_id}/download/{filename}")
async def download_file(
    job_id: str,
    filename: str,
    job_service: JobService = Depends()
):
    """Download a specific generated file"""
    
    job_data = await job_service.get_job_status(job_id)
    
    if not job_data:
        raise HTTPException(404, f"Job {job_id} not found")
    
    # Find file
    files = job_data.get('generated_files', [])
    file_path = None
    
    for f in files:
        if Path(f).name == filename:
            file_path = Path(f)
            break
    
    if not file_path or not file_path.exists():
        raise HTTPException(404, f"File {filename} not found")
    
    return FileResponse(
        path=str(file_path),
        filename=filename,
        media_type='application/octet-stream'
    )
```

#### Acceptance Criteria

- ✅ Job status retrieved correctly
- ✅ Results returned in JSON format
- ✅ File download works
- ✅ File listing shows all generated files
- ✅ Proper error handling for missing jobs

---

### Phase 2D.5: Historical & Comparison Endpoints (Week 2, Days 3-4)

**Objective**: Expose Phase 2B data through API

#### Tasks

1. **Historical Data Endpoints** (`src/api/routes/historical.py`)
   - `GET /api/historical/{ticker}` - Get all analyses for company
   - `GET /api/historical/{ticker}/trends` - Get trend data
   - `GET /api/historical/{ticker}/quarters` - Get quarterly breakdown

2. **Comparison Endpoints** (`src/api/routes/comparison.py`)
   - `GET /api/comparison/peers/{ticker}` - Get peer companies
   - `GET /api/comparison/sector/{sector}` - Get sector benchmarks
   - `POST /api/comparison/custom` - Custom comparison

#### Files to Create

```python
# src/api/routes/historical.py
from fastapi import APIRouter, HTTPException, Depends
from src.database.repository import DatabaseRepository
from config.settings import settings
from typing import List, Optional

router = APIRouter()

@router.get("/{ticker}")
async def get_company_history(
    ticker: str,
    limit: Optional[int] = 20
):
    """Get analysis history for a company"""
    
    repository = DatabaseRepository(settings.DATABASE_URL)
    results = repository.get_company_history(ticker, limit=limit)
    
    if not results:
        raise HTTPException(404, f"No data found for ticker {ticker}")
    
    return {
        'ticker': ticker,
        'count': len(results),
        'analyses': [
            {
                'id': r.id,
                'company_name': r.company_name,
                'quarter': r.quarter,
                'year': r.year,
                'analysis_date': r.analysis_date.isoformat(),
                'sentiment': r.analysis_data.get('sentiment', {}),
                'complexity': r.analysis_data.get('complexity', {}),
                'numerical': r.analysis_data.get('numerical', {}),
                'deception': r.analysis_data.get('deception', {})
            }
            for r in results
        ]
    }

@router.get("/{ticker}/trends")
async def get_trends(ticker: str):
    """Get trend analysis for a company"""
    
    repository = DatabaseRepository(settings.DATABASE_URL)
    
    # Get historical data
    history = repository.get_company_history(ticker, limit=8)
    
    if len(history) < 2:
        raise HTTPException(400, "Need at least 2 quarters for trend analysis")
    
    # Calculate trends
    trends = {
        'sentiment_trend': [],
        'complexity_trend': [],
        'deception_trend': []
    }
    
    for result in history:
        quarter_label = f"{result.quarter} {result.year}"
        
        trends['sentiment_trend'].append({
            'quarter': quarter_label,
            'net_positivity': result.analysis_data.get('sentiment', {}).get('net_positivity', 0)
        })
        
        trends['complexity_trend'].append({
            'quarter': quarter_label,
            'composite_score': result.analysis_data.get('complexity', {}).get('composite', 0)
        })
        
        if 'deception' in result.analysis_data:
            trends['deception_trend'].append({
                'quarter': quarter_label,
                'risk_score': result.analysis_data['deception'].get('overall_risk_score', 0)
            })
    
    return {
        'ticker': ticker,
        'quarters_analyzed': len(history),
        'trends': trends
    }
```

```python
# src/api/routes/comparison.py
from fastapi import APIRouter, HTTPException
from src.database.repository import DatabaseRepository
from config.settings import settings
from pydantic import BaseModel
from typing import List

router = APIRouter()

class ComparisonRequest(BaseModel):
    tickers: List[str]
    quarter: str
    year: int

@router.get("/peers/{ticker}")
async def get_peer_comparison(
    ticker: str,
    quarter: str,
    year: int
):
    """Compare company with sector peers"""
    
    repository = DatabaseRepository(settings.DATABASE_URL)
    
    # Get company analysis
    company_result = repository.get_analysis(ticker, quarter, year)
    if not company_result:
        raise HTTPException(404, f"No analysis found for {ticker} {quarter} {year}")
    
    # Get sector
    company = repository.get_company_by_ticker(ticker)
    if not company or not company.sector:
        raise HTTPException(404, "Company sector information not available")
    
    # Get sector peers
    peer_results = repository.get_sector_analyses(company.sector, quarter, year)
    
    return {
        'ticker': ticker,
        'company_name': company_result.company_name,
        'sector': company.sector,
        'quarter': quarter,
        'year': year,
        'company_metrics': {
            'sentiment': company_result.analysis_data.get('sentiment', {}),
            'complexity': company_result.analysis_data.get('complexity', {}),
            'deception': company_result.analysis_data.get('deception', {})
        },
        'sector_averages': _calculate_sector_averages(peer_results),
        'peer_count': len(peer_results)
    }

def _calculate_sector_averages(results):
    """Calculate average metrics across peers"""
    if not results:
        return {}
    
    total = len(results)
    avg_sentiment = sum(r.analysis_data.get('sentiment', {}).get('net_positivity', 0) for r in results) / total
    avg_complexity = sum(r.analysis_data.get('complexity', {}).get('composite', 0) for r in results) / total
    avg_deception = sum(r.analysis_data.get('deception', {}).get('overall_risk_score', 0) for r in results) / total
    
    return {
        'sentiment': {'net_positivity': avg_sentiment},
        'complexity': {'composite': avg_complexity},
        'deception': {'overall_risk_score': avg_deception}
    }

@router.post("/custom")
async def custom_comparison(request: ComparisonRequest):
    """Compare multiple companies"""
    
    repository = DatabaseRepository(settings.DATABASE_URL)
    
    results = []
    for ticker in request.tickers:
        result = repository.get_analysis(ticker, request.quarter, request.year)
        if result:
            results.append({
                'ticker': ticker,
                'company_name': result.company_name,
                'metrics': {
                    'sentiment': result.analysis_data.get('sentiment', {}),
                    'complexity': result.analysis_data.get('complexity', {}),
                    'deception': result.analysis_data.get('deception', {})
                }
            })
    
    return {
        'quarter': request.quarter,
        'year': request.year,
        'companies': results,
        'count': len(results)
    }
```

#### Acceptance Criteria

- ✅ Historical data retrieved correctly
- ✅ Trends calculated accurately
- ✅ Peer comparison works
- ✅ Sector benchmarks returned
- ✅ Custom comparison handles multiple tickers

---

### Phase 2D.6: Web Interface (Week 2, Days 5-7)

**Objective**: Build user-friendly web interface

#### Tasks

1. **HTML Templates** (`src/web/templates/`)
   - Main dashboard
   - Upload interface
   - Results display
   - History view

2. **Static Assets** (`src/web/static/`)
   - CSS styling
   - JavaScript for interactivity
   - AJAX for API calls

3. **Frontend Routes** (Add to `app.py`)
   - Serve HTML pages
   - Handle form submissions

#### Files to Create

```html
<!-- src/web/templates/index.html -->
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Earnings Call Analyzer</title>
    <link rel="stylesheet" href="/static/css/styles.css">
</head>
<body>
    <div class="container">
        <header>
            <h1>📊 Earnings Call Analyzer</h1>
            <p>Advanced transcript analysis with deception detection</p>
        </header>
        
        <nav>
            <a href="/" class="active">Dashboard</a>
            <a href="/upload">Upload</a>
            <a href="/history">History</a>
            <a href="/docs" target="_blank">API Docs</a>
        </nav>
        
        <main>
            <section class="stats">
                <div class="stat-card">
                    <h3>Total Analyses</h3>
                    <p id="total-analyses">0</p>
                </div>
                <div class="stat-card">
                    <h3>Pending Jobs</h3>
                    <p id="pending-jobs">0</p>
                </div>
                <div class="stat-card">
                    <h3>Companies Tracked</h3>
                    <p id="companies-count">0</p>
                </div>
            </section>
            
            <section class="recent-analyses">
                <h2>Recent Analyses</h2>
                <div id="recent-list"></div>
            </section>
        </main>
    </div>
    
    <script src="/static/js/main.js"></script>
</body>
</html>
```

```html
<!-- src/web/templates/upload.html -->
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Upload Transcript - Earnings Call Analyzer</title>
    <link rel="stylesheet" href="/static/css/styles.css">
</head>
<body>
    <div class="container">
        <header>
            <h1>📤 Upload Transcript</h1>
        </header>
        
        <nav>
            <a href="/">Dashboard</a>
            <a href="/upload" class="active">Upload</a>
            <a href="/history">History</a>
        </nav>
        
        <main>
            <form id="upload-form" enctype="multipart/form-data">
                <div class="form-group">
                    <label for="company_name">Company Name*</label>
                    <input type="text" id="company_name" name="company_name" required>
                </div>
                
                <div class="form-group">
                    <label for="ticker">Ticker Symbol*</label>
                    <input type="text" id="ticker" name="ticker" required>
                </div>
                
                <div class="form-row">
                    <div class="form-group">
                        <label for="quarter">Quarter*</label>
                        <select id="quarter" name="quarter" required>
                            <option value="Q1">Q1</option>
                            <option value="Q2">Q2</option>
                            <option value="Q3">Q3</option>
                            <option value="Q4">Q4</option>
                        </select>
                    </div>
                    
                    <div class="form-group">
                        <label for="year">Year*</label>
                        <input type="number" id="year" name="year" min="2000" max="2100" required>
                    </div>
                </div>
                
                <div class="form-group">
                    <label for="file">Transcript File*</label>
                    <input type="file" id="file" name="file" accept=".txt,.pdf" required>
                    <small>Supported formats: .txt, .pdf</small>
                </div>
                
                <div class="form-group">
                    <label>Output Formats</label>
                    <label><input type="checkbox" name="format" value="json" checked> JSON</label>
                    <label><input type="checkbox" name="format" value="pdf"> PDF Report</label>
                    <label><input type="checkbox" name="format" value="html"> HTML Dashboard</label>
                    <label><input type="checkbox" name="format" value="excel"> Excel Workbook</label>
                </div>
                
                <div class="form-group">
                    <label><input type="checkbox" name="enable_deception" checked> Enable Deception Detection</label>
                </div>
                
                <button type="submit" class="btn-primary">Analyze Transcript</button>
            </form>
            
            <div id="upload-status" style="display: none;">
                <h3>Upload Status</h3>
                <p id="status-message"></p>
                <div id="job-link"></div>
            </div>
        </main>
    </div>
    
    <script src="/static/js/upload.js"></script>
</body>
</html>
```

```css
/* src/web/static/css/styles.css */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    background: #f5f7fa;
    color: #333;
    line-height: 1.6;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
}

header {
    text-align: center;
    padding: 40px 0;
    background: white;
    border-radius: 10px;
    margin-bottom: 20px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

header h1 {
    color: #2c3e50;
    margin-bottom: 10px;
}

nav {
    display: flex;
    gap: 10px;
    margin-bottom: 30px;
    background: white;
    padding: 15px;
    border-radius: 10px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

nav a {
    padding: 10px 20px;
    text-decoration: none;
    color: #666;
    border-radius: 5px;
    transition: all 0.3s;
}

nav a:hover, nav a.active {
    background: #3498db;
    color: white;
}

.stats {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 20px;
    margin-bottom: 30px;
}

.stat-card {
    background: white;
    padding: 30px;
    border-radius: 10px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    text-align: center;
}

.stat-card h3 {
    color: #666;
    font-size: 14px;
    text-transform: uppercase;
    margin-bottom: 10px;
}

.stat-card p {
    font-size: 36px;
    font-weight: bold;
    color: #3498db;
}

.form-group {
    margin-bottom: 20px;
}

.form-group label {
    display: block;
    margin-bottom: 5px;
    font-weight: 600;
    color: #555;
}

.form-group input[type="text"],
.form-group input[type="number"],
.form-group input[type="file"],
.form-group select {
    width: 100%;
    padding: 10px;
    border: 1px solid #ddd;
    border-radius: 5px;
    font-size: 14px;
}

.form-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20px;
}

.btn-primary {
    background: #3498db;
    color: white;
    padding: 12px 30px;
    border: none;
    border-radius: 5px;
    font-size: 16px;
    cursor: pointer;
    transition: background 0.3s;
}

.btn-primary:hover {
    background: #2980b9;
}

#upload-status {
    margin-top: 30px;
    padding: 20px;
    background: #d4edda;
    border: 1px solid #c3e6cb;
    border-radius: 5px;
}
```

```javascript
// src/web/static/js/upload.js
document.getElementById('upload-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const formData = new FormData();
    formData.append('file', document.getElementById('file').files[0]);
    formData.append('company_name', document.getElementById('company_name').value);
    formData.append('ticker', document.getElementById('ticker').value);
    formData.append('quarter', document.getElementById('quarter').value);
    formData.append('year', document.getElementById('year').value);
    
    // Get output formats
    const formats = Array.from(document.querySelectorAll('input[name="format"]:checked'))
        .map(cb => cb.value);
    formData.append('output_formats', formats.join(','));
    
    const enableDeception = document.querySelector('input[name="enable_deception"]').checked;
    formData.append('enable_deception', enableDeception);
    
    // Show loading
    document.getElementById('upload-status').style.display = 'block';
    document.getElementById('status-message').textContent = 'Uploading...';
    
    try {
        const response = await fetch('/api/analyze/upload', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (response.ok) {
            document.getElementById('status-message').textContent = 
                'Upload successful! Job queued for processing.';
            document.getElementById('job-link').innerHTML = 
                `<a href="/results?job_id=${data.job_id}">View Job Status</a>`;
        } else {
            document.getElementById('status-message').textContent = 
                'Error: ' + (data.detail || 'Upload failed');
        }
    } catch (error) {
        document.getElementById('status-message').textContent = 
            'Error: ' + error.message;
    }
});
```

#### Acceptance Criteria

- ✅ Dashboard displays correctly
- ✅ Upload form works
- ✅ File uploads successfully
- ✅ Job status displayed
- ✅ Results page shows analysis data
- ✅ Responsive design

---

### Phase 2D.7: Testing & Documentation (Week 3)

**Objective**: Comprehensive testing and documentation

#### Tasks

1. **API Tests** (`tests/test_api.py`)
   - Test all endpoints
   - Test error handling
   - Test file uploads
   - Test job lifecycle

2. **Integration Tests** (`tests/test_integration.py`)
   - End-to-end workflow tests
   - Multi-format output tests
   - Database integration tests

3. **Documentation**
   - API documentation (OpenAPI/Swagger)
   - Deployment guide
   - User guide
   - Developer guide

#### Files to Create

```python
# tests/test_api.py
import pytest
from fastapi.testclient import TestClient
from src.api.app import app
from pathlib import Path

client = TestClient(app)

def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert "status" in response.json()

def test_upload_transcript():
    """Test transcript upload"""
    test_file = Path("tests/data/sample_transcript.txt")
    
    with open(test_file, "rb") as f:
        response = client.post(
            "/api/analyze/upload",
            files={"file": ("transcript.txt", f, "text/plain")},
            data={
                "company_name": "Test Corp",
                "ticker": "TEST",
                "quarter": "Q4",
                "year": 2024,
                "output_formats": "json,pdf"
            }
        )
    
    assert response.status_code == 200
    data = response.json()
    assert "job_id" in data
    assert data["status"] == "pending"

def test_get_job_status():
    """Test job status retrieval"""
    # First create a job
    test_file = Path("tests/data/sample_transcript.txt")
    
    with open(test_file, "rb") as f:
        upload_response = client.post(
            "/api/analyze/upload",
            files={"file": ("transcript.txt", f, "text/plain")},
            data={
                "company_name": "Test Corp",
                "ticker": "TEST",
                "quarter": "Q4",
                "year": 2024
            }
        )
    
    job_id = upload_response.json()["job_id"]
    
    # Get job status
    response = client.get(f"/api/jobs/{job_id}")
    assert response.status_code == 200
    assert response.json()["job_id"] == job_id

def test_list_jobs():
    """Test job listing"""
    response = client.get("/api/jobs")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_invalid_file_type():
    """Test rejection of invalid file types"""
    response = client.post(
        "/api/analyze/upload",
        files={"file": ("test.exe", b"content", "application/octet-stream")},
        data={
            "company_name": "Test Corp",
            "ticker": "TEST",
            "quarter": "Q4",
            "year": 2024
        }
    )
    assert response.status_code == 400

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

#### Acceptance Criteria

- ✅ All API tests pass
- ✅ Integration tests pass
- ✅ Code coverage > 80%
- ✅ API documentation complete
- ✅ Deployment guide written
- ✅ User guide complete

---

## API Endpoints Specification

### Analysis Endpoints

| Method | Endpoint | Description | Request | Response |
|--------|----------|-------------|---------|----------|
| POST | `/api/analyze/upload` | Upload file for analysis | FormData with file + metadata | JobResponse |
| POST | `/api/analyze/text` | Submit text for analysis | AnalysisRequest + text | JobResponse |
| GET | `/api/analyze/supported-formats` | List supported formats | - | Formats list |

### Job Management Endpoints

| Method | Endpoint | Description | Request | Response |
|--------|----------|-------------|---------|----------|
| GET | `/api/jobs/{job_id}` | Get job status | - | JobResponse |
| GET | `/api/jobs` | List all jobs | ?status=pending | List[JobResponse] |
| DELETE | `/api/jobs/{job_id}` | Delete job | - | Success message |

### Results Endpoints

| Method | Endpoint | Description | Request | Response |
|--------|----------|-------------|---------|----------|
| GET | `/api/results/{job_id}` | Get results (JSON) | - | AnalysisResult |
| GET | `/api/results/{job_id}/files` | List generated files | - | File list |
| GET | `/api/results/{job_id}/download/{filename}` | Download file | - | File |

### Historical Data Endpoints

| Method | Endpoint | Description | Request | Response |
|--------|----------|-------------|---------|----------|
| GET | `/api/historical/{ticker}` | Get company history | ?limit=20 | Analysis list |
| GET | `/api/historical/{ticker}/trends` | Get trend data | - | Trend analysis |
| GET | `/api/historical/{ticker}/quarters` | Get quarterly data | - | Quarterly breakdown |

### Comparison Endpoints

| Method | Endpoint | Description | Request | Response |
|--------|----------|-------------|---------|----------|
| GET | `/api/comparison/peers/{ticker}` | Compare with peers | ?quarter=Q4&year=2024 | Peer comparison |
| GET | `/api/comparison/sector/{sector}` | Get sector benchmarks | ?quarter=Q4&year=2024 | Sector data |
| POST | `/api/comparison/custom` | Custom comparison | ComparisonRequest | Comparison results |

### Health Check Endpoints

| Method | Endpoint | Description | Request | Response |
|--------|----------|-------------|---------|----------|
| GET | `/health` | Basic health check | - | Status |
| GET | `/health/detailed` | Detailed health check | - | System status |

---

## Data Models

### Request Models

```python
class AnalysisRequest(BaseModel):
    company_name: str
    ticker: str
    quarter: str  # Q1, Q2, Q3, Q4
    year: int
    output_formats: List[OutputFormat]
    enable_deception: bool = True

class ComparisonRequest(BaseModel):
    tickers: List[str]
    quarter: str
    year: int
```

### Response Models

```python
class JobResponse(BaseModel):
    job_id: str
    status: JobStatus  # pending, processing, completed, failed
    created_at: datetime
    updated_at: datetime
    progress: Optional[int]
    message: Optional[str]

class AnalysisResultResponse(BaseModel):
    job_id: str
    company_name: str
    ticker: str
    quarter: str
    year: int
    analysis_data: Dict[str, Any]
    generated_files: List[str]
    completed_at: datetime
```

---

## Web Interface Design

### Pages

1. **Dashboard** (`/`)
   - Recent analyses
   - Statistics
   - Quick actions

2. **Upload** (`/upload`)
   - File upload form
   - Metadata input
   - Format selection

3. **Results** (`/results?job_id=...`)
   - Analysis display
   - Download links
   - Visualizations

4. **History** (`/history`)
   - Company search
   - Historical view
   - Trend charts

---

## Testing Strategy

### Unit Tests

- Test individual API endpoints
- Test services in isolation
- Test data models
- Test file operations

### Integration Tests

- End-to-end workflow
- Database integration
- File upload → analysis → results
- Multi-format output

### Performance Tests

- Concurrent request handling
- Large file uploads
- Long-running jobs
- Database query performance

---

## Deployment Considerations

### Environment Variables

```bash
# .env
DATABASE_URL=sqlite:///data/earnings_analyzer.db
UPLOAD_DIR=data/uploads
OUTPUT_DIR=data/outputs
JOBS_DIR=data/jobs

# Optional: Redis for job queue
REDIS_URL=redis://localhost:6379

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=*
```

### Running the Application

```bash
# Install dependencies
pip install -r requirements-phase2d.txt

# Start the API server
uvicorn src.api.app:app --host 0.0.0.0 --port 8000

# Start the worker (in another terminal)
python src/jobs/worker.py
```

### Docker Deployment

```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements*.txt ./
RUN pip install -r requirements-phase2d.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "src.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
    environment:
      - DATABASE_URL=sqlite:///data/earnings_analyzer.db
  
  worker:
    build: .
    command: python src/jobs/worker.py
    volumes:
      - ./data:/app/data
    environment:
      - DATABASE_URL=sqlite:///data/earnings_analyzer.db
```

---

## Success Criteria

### Phase 2D Completion Checklist

- ✅ FastAPI application running
- ✅ All API endpoints implemented
- ✅ File upload working
- ✅ Job queue system operational
- ✅ Background worker processing jobs
- ✅ Results retrievable in multiple formats
- ✅ Historical data accessible via API
- ✅ Comparison endpoints working
- ✅ Web interface functional
- ✅ All tests passing
- ✅ API documentation complete
- ✅ Deployment guide written
- ✅ Can handle concurrent requests
- ✅ Error handling robust
- ✅ Logging configured

---

## Timeline & Milestones

### Week 1: Core API
- Days 1-3: API framework and models
- Days 4-5: File upload and analysis
- Days 6-7: Job queue system

### Week 2: Features & Interface
- Days 1-2: Results and job management
- Days 3-4: Historical and comparison
- Days 5-7: Web interface

### Week 3: Testing & Polish
- Days 1-2: Unit and integration tests
- Days 3-4: Documentation
- Days 5-7: Bug fixes and optimization

---

## Future Enhancements (Post Phase 2D)

### Phase 2E Integration
- Advanced analytics endpoints
- Predictive models
- Pattern recognition

### Potential Additions
- User authentication
- Rate limiting
- Caching layer (Redis)
- WebSocket for real-time updates
- Email notifications
- Scheduled analyses
- Batch processing
- Export to BI tools

---

## Support & Resources

### Documentation
- FastAPI Docs: https://fastapi.tiangolo.com/
- SQLAlchemy: https://docs.sqlalchemy.org/
- Plotly: https://plotly.com/python/

### Internal References
- Phase 2B Database: `PHASE_2B_COMPLETE.md`
- Phase 2C Reporting: `PHASE_2C_COMPLETE.md`
- Phase 2 Spec: `PHASE_2_SPECIFICATION.md`

---

## Notes for Implementation

1. **Start Simple**: Begin with basic functionality, then add complexity
2. **Test Early**: Write tests as you build each component
3. **Document**: Keep documentation up-to-date
4. **Iterate**: Get feedback and refine
5. **Monitor**: Track performance and errors

---

**Version:** 2.0.0-phase2d  
**Last Updated:** October 17, 2025  
**Status:** Ready for Implementation  
**Estimated Completion:** 3 weeks

---

## Quick Start Commands

```bash
# Setup
pip install -r requirements-phase2d.txt

# Run API
uvicorn src.api.app:app --reload

# Run Worker
python src/jobs/worker.py

# Run Tests
pytest tests/test_api.py -v

# View API Docs
# Navigate to http://localhost:8000/docs
```

---

**END OF PHASE 2D ROADMAP**
