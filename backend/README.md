# PlanWise Coach Backend

A FastAPI-based backend for the AI running coach application. This service provides AI-powered running plan generation, plan versioning, conversation memory, and RESTful API endpoints.

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- OpenAI API key

### Setup

1. **Create virtual environment:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment:**
   ```bash
   # Create .env file
   echo "OPENAI_API_KEY=your_api_key_here" > .env
   ```

4. **Run the server:**
   ```bash
   uvicorn app.main:app --reload
   ```

   The API will be available at `http://localhost:8000`

5. **View API documentation:**
   - Swagger UI: `http://localhost:8000/docs`
   - ReDoc: `http://localhost:8000/redoc`

## 📁 Project Structure

```
backend/
├── app/
│   ├── main.py          # FastAPI routes and application
│   ├── config.py        # Environment configuration
│   ├── db.py           # Database setup and connection
│   ├── models.py       # SQLAlchemy ORM models
│   ├── schemas.py      # Pydantic validation schemas
│   ├── crud.py         # Database CRUD operations
│   ├── deps.py         # Utilities and dependencies
│   ├── llm.py          # OpenAI integration
│   ├── prompts.py      # AI system prompts
│   ├── plan_utils.py   # Plan comparison and analysis
│   └── streaming.py    # Streaming response support (future)
├── tests/
│   └── test_plan_schema.py  # Pydantic schema tests
├── requirements.txt
└── README.md
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the backend directory:

```env
# Required
OPENAI_API_KEY=sk-...

# Optional (with defaults)
OPENAI_MODEL=gpt-4o                     # AI model to use
DB_URL=sqlite:///./coach.db             # Database connection
```

### AI Model Settings
- **Model**: GPT-4o for high-quality plan generation
- **Temperature**: 0.3 for balanced creativity and consistency
- **Max Tokens**: 4000 to ensure complete plan generation
- **Timeout**: 90 seconds for complex requests

## 📊 API Reference

### Health Check
```http
GET /health
```
**Response:** `{"status": "healthy"}`

### Chat with AI Coach
```http
POST /chat
Content-Type: application/json

{
  "client_id": "uuid-string",
  "message": "I want an 8-week half marathon plan"
}
```

**Response:**
```json
{
  "reply": "I've created a comprehensive 8-week half marathon plan...",
  "plan": {
    "meta": {
      "goal": "Half Marathon",
      "phase": "Base",
      "weekly_km_target": 50
    },
    "weeks": { ... }
  },
  "plan_updated": true
}
```

### Get Current Plan
```http
GET /plan?client_id=uuid-string
```

**Response:**
```json
{
  "plan": { /* Complete PlanDoc object */ },
  "version": 1,
  "created_at": "2024-01-01T00:00:00Z"
}
```

### Reset Session
```http
DELETE /session/{client_id}
```

Deletes all conversations and plans for the specified client.

**Response:**
```json
{
  "success": true,
  "message": "Session reset successfully",
  "conversations_deleted": 5,
  "plans_deleted": 2
}
```

## 🏗️ Architecture Deep Dive

### Core Components

#### 1. FastAPI Application (`main.py`)
- RESTful API endpoints with automatic OpenAPI documentation
- Structured error handling and logging
- CORS support for frontend integration

#### 2. LLM Integration (`llm.py`)
- OpenAI GPT-4 client with robust error handling
- Configurable timeouts and retry logic
- Response validation and parsing

#### 3. Database Layer (`models.py`, `crud.py`)
- SQLAlchemy ORM with SQLite (production-ready for PostgreSQL)
- Plan versioning with `is_current` flags
- Conversation history with role-based filtering

#### 4. Data Validation (`schemas.py`)
- Pydantic models for type-safe request/response handling
- Comprehensive plan structure validation
- Flexible constraints for different training goals

### Key Features

#### Plan Versioning System
```python
# Each plan modification creates a new version
def create_new_plan(db: Session, client_id: str, plan_json: dict) -> Plan:
    # Mark existing plans as not current
    db.query(Plan).filter(Plan.client_id == client_id).update({"is_current": False})
    
    # Create new plan with incremented version
    new_plan = Plan(
        client_id=client_id,
        plan_json=plan_json,
        version=get_next_version(db, client_id),
        is_current=True
    )
```

#### Context-Aware Conversations
The system builds intelligent context for the AI:
1. **System Prompt**: Core coaching instructions
2. **Current Plan Context**: Summary of active plan (if exists)
3. **Filtered History**: Recent relevant conversation messages
4. **Current Request**: User's latest message

#### Intelligent Message Filtering
```python
# Skip error messages, short responses, and previous plan JSON
if ("error" in content.lower() or 
    "sorry" in content.lower() or 
    (msg.role == "assistant" and len(content) < 50) or
    (msg.role == "assistant" and "PLAN" in content.upper())):
    continue  # Exclude from context
```

## 🧪 Testing

### Run Tests
```bash
python -m pytest tests/ -v
```

### Test Structure
- **Schema Validation**: Ensures plan structures meet requirements
- **Edge Cases**: Handles malformed inputs gracefully
- **Integration**: End-to-end API testing

### Adding Tests
```python
def test_new_feature():
    # Test implementation
    assert expected_behavior()
```

## 🔍 Debugging & Monitoring

### Logging
```python
import logging
logger = logging.getLogger(__name__)

# Usage throughout the application
logger.info(f"Processing request for client {client_id}")
logger.error(f"Failed to generate plan: {error}")
```

### Common Issues & Solutions

**OpenAI API Errors:**
- Verify API key in `.env` file
- Check rate limits and billing status
- Monitor model availability

**Database Issues:**
- Ensure SQLite file has write permissions
- Check for database locks during high concurrency
- Consider connection pooling for production

**Plan Generation:**
- Incomplete responses: Increased max_tokens to 4000
- Validation failures: Enhanced schema with detailed error messages
- Context overflow: Intelligent message filtering

## 🚀 Production Considerations

### Database Migration
```python
# Switch from SQLite to PostgreSQL
DB_URL = "postgresql://user:pass@localhost/planwise"

# Add connection pooling
engine = create_engine(
    DB_URL,
    pool_size=20,
    max_overflow=0,
    pool_pre_ping=True
)
```

### Security Enhancements
- API key rotation and secure storage
- Rate limiting per client
- Input sanitization and validation
- CORS configuration for production domains

### Performance Optimization
- Connection pooling for database
- Response caching for static content
- Async database operations
- Background task processing

### Monitoring & Observability
```python
# Add correlation IDs for request tracing
# Implement health checks with detailed status
# Set up error tracking (Sentry, etc.)
# Monitor OpenAI API usage and costs
```

## 🔄 Future Enhancements

### Planned Features
- **Streaming Responses**: Real-time plan generation with `streaming.py`
- **Multi-Model Support**: Fallback to different AI models
- **Advanced Analytics**: Plan effectiveness tracking
- **Integration APIs**: Strava, Garmin, etc.

### Extension Points
```python
# Custom training methodologies
class CustomTrainingPlan(BaseTrainingPlan):
    methodology: str = "Lydiard"  # Add training system support

# Race-specific optimization
class RaceOptimizedPlan(PlanDoc):
    race_strategy: RaceStrategy  # Pacing and tapering specifics

# Injury prevention
class InjuryAwarePlan(PlanDoc):
    injury_history: List[InjuryRecord]
    prevention_focus: List[str]
```

## 💡 Development Guidelines

### Code Style
- Follow PEP 8 with Black formatting
- Type hints on all functions
- Docstrings for public APIs
- Descriptive variable names

### Architecture Patterns
- **Dependency Injection**: Use FastAPI's dependency system
- **Separation of Concerns**: Keep routes, business logic, and data access separate
- **Error Handling**: Consistent exception handling with user-friendly messages
- **Logging**: Structured logging with appropriate levels

### Contributing
1. Fork the repository
2. Create a feature branch
3. Add comprehensive tests
4. Update documentation
5. Submit a pull request

The backend is designed for extensibility - new features should integrate cleanly with existing patterns and maintain type safety throughout. 