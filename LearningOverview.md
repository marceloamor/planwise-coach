# 🎓 Learning Overview: PlanWise Coach Technologies

This guide introduces the key technologies used in PlanWise Coach, explaining what each does and why we chose it. Use this as your roadmap for learning - understand the "why" first, then dive deeper into the "how."

## 🏗️ Architecture Pattern: Frontend-Backend Separation

### What It Is
We split our application into two independent services:
- **Frontend** (Next.js) - User interface running in the browser
- **Backend** (FastAPI) - API server handling business logic and data

### Why We Use It
- **Scalability**: Each service can be deployed and scaled independently
- **Technology Choice**: Best tool for each job (React for UI, Python for AI/data)
- **Team Development**: Frontend and backend teams can work in parallel
- **API-First**: Clean contract between services, easy to test and maintain

### What to Learn
- **REST API principles**: HTTP methods (GET, POST, DELETE), status codes, JSON
- **API design**: Creating clean, predictable endpoints
- **State management**: How frontend manages data from API calls

---

## 🚀 Backend Technologies

### FastAPI (Python Web Framework)

**What It Is**: Modern, fast web framework for building APIs with Python 3.7+

**Why We Chose It**:
- **Automatic API Documentation**: Generates OpenAPI/Swagger docs automatically
- **Type Safety**: Built-in support for Python type hints
- **Performance**: One of the fastest Python frameworks available
- **Async Support**: Native support for async/await patterns
- **Easy Testing**: Simple to write and run tests

**In Our Project**:
```python
@app.post("/chat", response_model=ChatResponse)
def chat_endpoint(message: ChatMessageIn):
    # FastAPI automatically validates input and output
    return {"reply": "...", "plan": plan_doc}
```

**What to Learn**:
- **Route decoration**: `@app.get()`, `@app.post()` patterns
- **Dependency injection**: FastAPI's dependency system
- **Request/response models**: Pydantic integration
- **Middleware**: CORS, authentication, logging
- **Error handling**: HTTPException and custom error responses

### SQLAlchemy (Database ORM)

**What It Is**: Object-Relational Mapping library that lets you work with databases using Python objects

**Why We Use It**:
- **Database Abstraction**: Same code works with SQLite, PostgreSQL, MySQL
- **Type Safety**: Python objects represent database tables
- **Migration Support**: Easy database schema changes
- **Relationship Management**: Handles foreign keys and joins automatically

**In Our Project**:
```python
class Plan(Base):
    __tablename__ = "plans"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    client_id: Mapped[str] = mapped_column(String(64), index=True)
    plan_json: Mapped[dict] = mapped_column(JSON)
```

**What to Learn**:
- **Models**: Defining database tables as Python classes
- **Relationships**: Foreign keys, one-to-many, many-to-many
- **Querying**: `db.query(Model).filter().all()` patterns
- **Sessions**: Database connections and transactions

### Pydantic (Data Validation)

**What It Is**: Data validation library using Python type annotations

**Why We Use It**:
- **Input Validation**: Ensures API receives correctly formatted data
- **Output Serialization**: Guarantees consistent API responses
- **Type Safety**: Catches data errors at runtime
- **Documentation**: Auto-generates API documentation

**In Our Project**:
```python
class PlanDoc(BaseModel):
    meta: PlanMeta
    constraints: PlanConstraints
    weeks: Dict[str, WeekPlan]
    
    @field_validator('weeks')
    def validate_weeks_structure(cls, v):
        # Custom validation logic
        return v
```

**What to Learn**:
- **Model definition**: Using BaseModel and Field()
- **Validators**: Custom validation functions
- **Serialization**: Converting between Python objects and JSON
- **Type hints**: Union types, Optional, List, Dict

### OpenAI API Integration

**What It Is**: Integration with OpenAI's GPT models for AI-powered plan generation

**Why We Use It**:
- **Natural Language**: Users can describe goals in plain English
- **Structured Output**: AI generates valid JSON plans
- **Conversational**: Chat-based interaction feels natural
- **Quality**: GPT-4 produces high-quality training plans

**In Our Project**:
```python
def chat_to_plan(messages: list[dict[str, str]]) -> str:
    resp = client.chat.completions.create(
        model="gpt-4o",
        temperature=0.3,
        messages=messages,
        max_tokens=4000
    )
    return resp.choices[0].message.content
```

**What to Learn**:
- **Prompt engineering**: Crafting effective system prompts
- **API usage**: Making requests, handling responses, error management
- **Context management**: Building conversation history
- **Cost optimization**: Token usage, model selection

---

## 🎨 Frontend Technologies

### Next.js (React Framework)

**What It Is**: Full-stack React framework with built-in optimizations and developer experience features

**Why We Chose It**:
- **App Router**: Modern file-based routing system
- **TypeScript**: Built-in TypeScript support
- **Performance**: Automatic code splitting, image optimization
- **Developer Experience**: Hot reload, error overlay, built-in linting

**In Our Project**:
```typescript
// app/page.tsx - Main application page
export default function Home() {
  return <ChatPanel />;
}

// Automatic routing based on file structure
```

**What to Learn**:
- **App Router**: File-based routing, layouts, pages
- **Server Components**: Rendering on the server vs client
- **API routes**: Creating backend endpoints in Next.js (we use separate backend instead)
- **Deployment**: Vercel, static export, Docker

### TypeScript (Type-Safe JavaScript)

**What It Is**: JavaScript with static type checking and modern language features

**Why We Use It**:
- **Catch Errors Early**: Find bugs before they reach production
- **Better IDE Support**: Autocomplete, refactoring, navigation
- **Self-Documenting**: Types serve as inline documentation
- **Refactoring Safety**: Rename variables/functions with confidence

**In Our Project**:
```typescript
interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
}

const [messages, setMessages] = useState<ChatMessage[]>([]);
```

**What to Learn**:
- **Basic types**: string, number, boolean, arrays, objects
- **Interfaces**: Defining object shapes
- **Union types**: Multiple possible types (`"user" | "assistant"`)
- **Generics**: Reusable type definitions (`useState<T>`)
- **Type guards**: Runtime type checking

### React Hooks (State Management)

**What It Is**: Functions that let you use state and other React features in functional components

**Why We Use Them**:
- **Simple State**: Easy to understand and test
- **Composition**: Combine hooks for complex behavior
- **Performance**: Fine-grained control over re-renders
- **Modern React**: Current best practice approach

**In Our Project**:
```typescript
const [currentPlan, setCurrentPlan] = useState<PlanDoc | null>(null);
const [loading, setLoading] = useState(false);

useEffect(() => {
  // Load plan when component mounts
  fetchPlan(clientId).then(setCurrentPlan);
}, [clientId]);
```

**What to Learn**:
- **useState**: Managing component state
- **useEffect**: Side effects, cleanup, dependencies
- **useCallback**: Optimizing function references
- **useRef**: Direct DOM access and persistent values
- **Custom hooks**: Creating reusable stateful logic

---

## 🔧 Development & Deployment Tools

### Virtual Environments (Python)

**What It Is**: Isolated Python environments for each project

**Why Essential**:
- **Dependency Isolation**: Each project has its own package versions
- **Reproducible**: Same environment across development and production
- **Clean Development**: Avoid conflicts between projects

**Usage**:
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
```

### Package Management

**Python (pip + requirements.txt)**:
- **requirements.txt**: Lists all Python dependencies with versions
- **pip**: Installs packages from PyPI
- **Version pinning**: Ensures reproducible installations

**Node.js (npm + package.json)**:
- **package.json**: Project metadata and dependencies
- **package-lock.json**: Locks exact dependency versions
- **npm**: Installs packages from npm registry

### Environment Variables

**What They Are**: Configuration values stored outside your code

**Why Important**:
- **Security**: Keep API keys out of version control
- **Flexibility**: Different settings for development/production
- **12-Factor App**: Industry standard for cloud-native applications

**In Our Project**:
```bash
# Backend .env
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4o

# Frontend .env.local
NEXT_PUBLIC_API_BASE=http://localhost:8000
```

---

## 🎯 Learning Path Recommendations

### 1. Start with the Basics (Week 1-2)
- **HTTP/REST APIs**: How web services communicate
- **JSON**: Data format for API requests/responses
- **Git**: Version control basics (clone, commit, push, pull)
- **Command line**: Basic terminal navigation and commands

### 2. Backend Fundamentals (Week 3-4)
- **Python basics**: If not already familiar
- **FastAPI tutorial**: Official documentation and tutorial
- **Database basics**: SQL fundamentals, CRUD operations
- **API testing**: Using curl, Postman, or browser dev tools

### 3. Frontend Essentials (Week 5-6)
- **React basics**: Components, props, state
- **TypeScript fundamentals**: Types, interfaces, basic patterns
- **Next.js tutorial**: App router, pages, routing
- **CSS/Styling**: Responsive design, flexbox, CSS modules

### 4. Integration & Advanced Topics (Week 7-8)
- **OpenAI API**: Prompt engineering, API usage patterns
- **Error handling**: Frontend and backend error patterns
- **Testing**: Writing unit tests for both frontend and backend
- **Deployment**: Docker, cloud platforms, environment setup

### 5. Project-Specific Learning (Week 9+)
- **Conversation systems**: Managing chat state and context
- **Data modeling**: Plan structures, versioning strategies
- **AI integration**: Working with LLM responses, structured output
- **User experience**: Progressive enhancement, loading states

---

## 🔍 Key Concepts to Master

### API Design Patterns
- **RESTful principles**: Resource-based URLs, HTTP methods
- **Request/response cycles**: Headers, body, status codes
- **Error handling**: Consistent error formats across endpoints
- **Documentation**: OpenAPI/Swagger specification

### State Management
- **Frontend state**: Component state vs application state
- **Server state**: Caching, invalidation, optimistic updates
- **Database state**: Transactions, consistency, relationships

### Type Safety
- **Schema validation**: Input validation with Pydantic
- **Type checking**: TypeScript compilation
- **Runtime safety**: Error boundaries, graceful degradation

### Development Workflow
- **Local development**: Running services, hot reload, debugging
- **Testing strategy**: Unit tests, integration tests, manual testing
- **Code quality**: Linting, formatting, type checking
- **Deployment pipeline**: Build, test, deploy automation

---

## 🎉 Getting Started

1. **Clone the repository** and follow the main README setup instructions
2. **Run both services** (backend and frontend) and explore the working application
3. **Read through the code** starting with the main entry points:
   - `backend/app/main.py` - API endpoints
   - `frontend/app/page.tsx` - Main UI component
4. **Make small changes** to understand how data flows through the system
5. **Pick a technology** from above and spend a week diving deep into its documentation
6. **Build a small feature** to practice integrating multiple technologies

Remember: The best way to learn is by building. Start with small changes and gradually take on larger features as you become more comfortable with each technology! 🚀 