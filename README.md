# AI SQL Chatbot

An AI-powered application that converts natural language questions into SQL queries, executes them against a PostgreSQL database, and provides intelligent analysis of results.

## Features

- Multi-language support (English, German, French, Spanish, Arabic, Urdu)
- Read-only SQL operations with injection protection
- Real-time query execution and results display
- Database schema exploration
- CSV export functionality
- Session state management
- JSON-structured AI responses

## Tech Stack

- **Frontend**: Streamlit
- **Backend**: FastAPI
- **AI/LLM**: OpenAI GPT-4.1
- **Database**: PostgreSQL
- **Validation**: SQLParse
- **Database Client**: Asyncpg

## Architecture

### Frontend (Streamlit)

- Language selection interface
- Natural language query input
- SQL display toggle
- Results table with CSV export
- Database schema viewer
- Sample queries sidebar
- Real-time processing indicators

### Backend (FastAPI)

- `POST /query` - Natural language to SQL conversion and execution
- `GET /schema` - Database schema information
- `GET /health` - Backend health check
- Pydantic models for request/response validation
- Comprehensive logging system

### AI Integration

- OpenAI GPT-4.1 for text-to-SQL conversion & response formulation
- JSON-structured responses for reliability
- Multi-language prompt engineering
- Temperature control for consistent SQL generation

## Setup

### Prerequisites

- Python 3.8+
- PostgreSQL with Northwind database
- OpenAI API key

### Installation

1. Clone the repository and navigate to the project directory
2. Create and activate a virtual environment:

   ```bash
   python -m venv venv
   # Windows: venv\Scripts\activate
   # Linux/Mac: source venv/bin/activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Create `.env` file with your configuration:

   ```env
   OPENAI_API_KEY=your_api_key_here
   DATABASE_URL=postgresql://user:password@localhost:5432/northwind
   ```

5. Start the backend:

   ```bash
   uvicorn backend.main:app --reload
   ```

6. Start the frontend:

   ```bash
   streamlit run frontend/app.py
   ```

## Usage

1. Access the application at `http://localhost:8501`
2. Select your preferred language from the sidebar
3. Enter natural language questions about the Northwind database
4. View generated SQL queries (toggle in sidebar)
5. Export results as CSV if needed

Example queries:

- "Show me all customers from Germany"
- "What are the top 5 products by sales?"
- "List all employees and their territories"

## API Endpoints

Access interactive API docs at `http://localhost:8000/docs`

### POST /query

Request:

```json
{
  "query": "Show me customers from France",
  "language": "en"
}
```

Response:

```json
{
  "sql": "SELECT * FROM customers WHERE country = 'France'",
  "db_result": [{"customer_id": "ALFKI", "company_name": "Alfreds Futterkiste"}],
  "answer": "{\"summary\": \"Found 11 customers from France including Alfreds Futterkiste...\"}",
  "error": ""
}
```

### GET /schema

Returns database schema with table and column information.

### GET /health

Returns backend service status and timestamp.
Returns:

```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:15.123456",
  "service": "AI SQL Chatbot Backend"
}
```

## License

MIT License
