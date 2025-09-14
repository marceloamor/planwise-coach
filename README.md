# 🏃‍♂️ PlanWise Coach

An AI-first running coach and training plan builder that generates personalized, adaptive training plans through natural conversation.

## ✨ Features

- **AI-Generated Plans**: Create complete 4-16 week training plans from simple prompts
- **Natural Conversation**: Chat with your AI coach to modify and refine plans
- **Plan Versioning**: Keep track of plan iterations and modifications
- **Anonymous Sessions**: No authentication required - uses device-specific client IDs
- **Real-time Updates**: Plans update instantly based on your feedback
- **Extensible Architecture**: Clean, modular codebase ready for enhancement

## 🚀 Quick Start

### Prerequisites

- **Node.js** 18+ (for frontend)
- **Python** 3.11+ (for backend)
- **OpenAI API Key** (get from [OpenAI Platform](https://platform.openai.com/api-keys))

### 1. Clone & Setup

```bash
git clone <repository-url>
cd planwise-coach
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create environment file
echo "OPENAI_API_KEY=your_api_key_here" > .env

# Run backend
uvicorn app.main:app --reload
```

Backend will be available at `http://localhost:8000`

### 3. Frontend Setup

```bash
cd ../frontend

# Install dependencies
npm install

# Run frontend
npm run dev
```

Frontend will be available at `http://localhost:3000`

### 4. Start Coaching!

1. Open `http://localhost:3000` in your browser
2. Type: `"I want an 8-week half marathon plan"`
3. Chat with your AI coach to refine the plan
4. Use "Start Over" to reset and try different goals

## 🏗️ Architecture

### Backend (`/backend`)
- **FastAPI** web framework with async support
- **SQLAlchemy** ORM with SQLite database
- **OpenAI GPT-4** for plan generation
- **Pydantic** for data validation and serialization

### Frontend (`/frontend`)
- **Next.js 14** with App Router
- **TypeScript** for type safety
- **React Query** for API state management
- **Modern CSS** with responsive design

### Key Components

```
backend/
├── app/
│   ├── main.py          # FastAPI routes
│   ├── models.py        # Database models
│   ├── schemas.py       # Pydantic schemas
│   ├── llm.py          # OpenAI integration
│   ├── prompts.py      # AI system prompts
│   └── crud.py         # Database operations
└── requirements.txt

frontend/
├── app/
│   ├── page.tsx        # Main application page
│   └── api.ts          # Backend API client
├── components/
│   ├── chat-panel.tsx  # Main chat interface
│   └── plan-card.tsx   # Training plan display
└── lib/
    └── anon-id.ts      # Anonymous client ID management
```

## 🔧 Configuration

### Environment Variables

**Backend** (`.env` in `/backend`):
```env
OPENAI_API_KEY=sk-...                    # Required: Your OpenAI API key
OPENAI_MODEL=gpt-4o                      # Optional: Model to use (default: gpt-4o)
DB_URL=sqlite:///./coach.db              # Optional: Database URL
```

### Features Toggles

- **Model Temperature**: Currently set to `0.3` for balanced creativity/consistency
- **Conversation Memory**: Stores last 10 messages per session
- **Plan Versioning**: Automatically creates new versions for significant changes

## 📊 API Endpoints

### Chat
```http
POST /chat
Content-Type: application/json

{
  "client_id": "uuid",
  "message": "I want a 10K plan"
}
```

### Get Current Plan
```http
GET /plan?client_id=uuid
```

### Reset Session
```http
DELETE /session/{client_id}
```

### Health Check
```http
GET /health
```

## 🧪 Development

### Running Tests
```bash
cd backend
python -m pytest tests/
```

### Code Quality
The codebase follows these principles:
- **Type Safety**: Full TypeScript/Pydantic typing
- **Error Handling**: Graceful fallbacks and user-friendly errors
- **Logging**: Structured logging for debugging and monitoring
- **Modularity**: Clean separation of concerns

### Adding Features

Common extension points:
- **New Plan Types**: Modify `schemas.py` and `prompts.py`
- **Different AI Models**: Update `config.py` and `llm.py`
- **Enhanced UI**: Add components in `/frontend/components`
- **Additional APIs**: Extend routes in `main.py`

## 🚦 Production Considerations

### Security
- Add authentication/authorization
- Implement rate limiting
- Validate/sanitize all inputs
- Use environment-specific secrets

### Performance
- Switch to PostgreSQL for production
- Add Redis for session caching
- Implement proper connection pooling
- Consider CDN for frontend assets

### Monitoring
- Add structured logging with correlation IDs
- Implement health checks and metrics
- Set up error tracking (e.g., Sentry)
- Monitor API usage and costs

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📝 License

MIT License - feel free to use this code for your own projects!

## 🏃‍♂️ Happy Training!

Built with ❤️ for runners who want AI-powered coaching without the complexity.
