# GenAI-Powered Sales & Marketing Intelligence Platform

A production-ready MVP of an AI-powered sales and marketing intelligence platform built with Next.js, FastAPI, PostgreSQL, and OpenAI.

## Features

### Core Functionality
- **User Management**: Role-based authentication (Admin, Sales, Marketing) with JWT
- **Lead Management**: CRUD operations, CSV bulk import, AI-powered lead scoring
- **Customer Management**: Convert leads to customers, track lifetime value
- **Campaign Management**: Create and track marketing campaigns with performance metrics
- **Sales Pipeline**: Manage deals through various stages with probability tracking

### AI Features (Powered by OpenAI GPT-4)
- **AI Lead Scoring**: Intelligent scoring (0-100) with reasoning and recommendations
- **Conversational Sales Agent**: Natural language queries converted to SQL
- **AI Insights Generator**: Weekly sales summaries, campaign performance, revenue forecasts
- **Marketing Content Generator**: Generate content variations for LinkedIn, Email, Twitter, etc.
- **RAG Implementation**: Semantic search using pgvector for context-aware responses

### Dashboard
- KPI cards (Revenue, Conversion Rate, Pipeline Value, etc.)
- Revenue over time charts
- Lead conversion funnel
- Campaign performance analytics
- Lead source distribution

## Tech Stack

### Backend
- **FastAPI** (Python) - High-performance async API framework
- **SQLAlchemy** - ORM for database operations
- **PostgreSQL** - Primary database
- **pgvector** - Vector similarity search for RAG
- **OpenAI API** - GPT-4 for AI features

### Frontend
- **Next.js 14** (App Router) - React framework
- **TypeScript** - Type safety
- **TailwindCSS** - Styling
- **Recharts** - Data visualization
- **Lucide React** - Icons

## Project Structure

```
├── backend/
│   ├── app/
│   │   ├── api/           # API routes
│   │   │   ├── auth.py    # Authentication endpoints
│   │   │   ├── leads.py   # Lead CRUD + CSV upload
│   │   │   ├── customers.py
│   │   │   ├── campaigns.py
│   │   │   ├── sales_records.py
│   │   │   ├── dashboard.py
│   │   │   └── ai.py      # AI feature endpoints
│   │   ├── core/          # Config, security, database
│   │   ├── models/        # SQLAlchemy models
│   │   ├── schemas/       # Pydantic schemas
│   │   └── services/      # Business logic
│   │       ├── openai_client.py
│   │       ├── lead_scoring.py
│   │       ├── chat_agent.py
│   │       ├── content_generator.py
│   │       ├── insights_generator.py
│   │       └── vector_store.py
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── app/           # Next.js App Router
│   │   │   ├── dashboard/ # Protected dashboard pages
│   │   │   └── page.tsx   # Login page
│   │   ├── components/    # Reusable components
│   │   ├── lib/           # API client, utilities
│   │   └── types/         # TypeScript types
│   ├── Dockerfile
│   └── package.json
├── docker-compose.yml
└── README.md
```

## Getting Started

### Prerequisites
- Docker and Docker Compose
- Node.js 20+ (for local frontend development)
- Python 3.11+ (for local backend development)
- OpenAI API key

### Quick Start with Docker

1. Clone the repository and navigate to the project directory

2. Create environment file:
```bash
cp .env.example .env
```

3. Add your OpenAI API key to `.env`:
```
OPENAI_API_KEY=sk-your-api-key-here
```

4. Start all services:
```bash
docker-compose up -d
```

5. Access the application:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

### Local Development

#### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env
# Edit .env with your configuration

# Run the server
uvicorn app.main:app --reload
```

#### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Copy environment file
cp .env.example .env.local

# Run development server
npm run dev
```

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login and get JWT token
- `GET /api/auth/me` - Get current user

### Leads
- `GET /api/leads` - List leads
- `POST /api/leads` - Create lead
- `GET /api/leads/{id}` - Get lead
- `PUT /api/leads/{id}` - Update lead
- `DELETE /api/leads/{id}` - Delete lead
- `POST /api/leads/upload-csv` - Bulk upload leads

### AI Features
- `POST /api/ai/score-lead` - AI lead scoring
- `POST /api/ai/chat` - Conversational data agent
- `POST /api/ai/generate-content` - Marketing content generation
- `POST /api/ai/insights` - Generate business insights
- `POST /api/ai/semantic-search` - RAG semantic search

### Dashboard
- `GET /api/dashboard/kpis` - Key performance indicators
- `GET /api/dashboard/revenue-over-time` - Revenue chart data
- `GET /api/dashboard/lead-funnel` - Lead conversion funnel
- `GET /api/dashboard/campaign-performance` - Campaign metrics

## Security Features

- JWT-based authentication with role-based access control
- SQL injection prevention (parameterized queries, query validation)
- Prompt injection prevention (system prompts, input sanitization)
- AI-generated SQL restricted to SELECT only
- Environment variable configuration (no hardcoded secrets)
- CORS configuration

## Database Schema

### Users
- id, email, hashed_password, full_name, role, is_active, timestamps

### Leads
- id, company_name, contact_name, email, phone, job_title
- industry, company_size, annual_revenue, location
- status, source, ai_score, ai_score_reasoning
- estimated_value, notes, assigned_to, timestamps

### Customers
- id, lead_id, company_name, contact_name, email, phone
- industry, company_size, location, status
- lifetime_value, total_purchases, timestamps

### Campaigns
- id, name, description, campaign_type, status
- target_audience, target_industry, budget, spent
- impressions, clicks, conversions, leads_generated
- revenue_attributed, calculated_metrics, timestamps

### Sales Records
- id, customer_id, sales_rep_id, deal_name, description
- amount, currency, stage, probability
- product_name, quantity, close_date, timestamps

### Vector Documents (RAG)
- id, content, document_type, source_id, source_table
- embedding (vector), metadata, timestamps

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| DATABASE_URL | PostgreSQL connection string | - |
| SECRET_KEY | JWT signing key | - |
| OPENAI_API_KEY | OpenAI API key | - |
| OPENAI_MODEL | OpenAI model to use | gpt-4o |
| CORS_ORIGINS | Allowed CORS origins | localhost:3000 |

## License

MIT License
