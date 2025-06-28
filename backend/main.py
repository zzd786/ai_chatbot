import datetime
import logging
from fastapi import FastAPI
from shared.config import logging_setup
from backend.llm import query_to_sql, answer_formulation
from backend.db import execute_sql_query, database_schema
from backend.models import QueryRequest, QueryResponse

# Start logging
logging_setup()
logger = logging.getLogger(__name__)

# Start FastAPI app
app = FastAPI()


# Status endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint to verify backend is running"""
    logger.info("Health check endpoint accessed")
    return {
        "status": "healthy",
        "timestamp": datetime.datetime.now().isoformat(),
        "service": "AI SQL Chatbot Backend",
    }


# Endpoint to handle user queries
@app.post("/query", response_model=QueryResponse)
async def query_endpoint(request: QueryRequest):
    """
    This endpoint handles user queries, converts them to SQL, executes the SQL query,
    and returns the results along with the generated SQL and formulated answer.

    Args:
        request (Request): It has user query and lang.
    Returns:
        dict: A {} with sql_query, db_result, answer, and error.
    """
    logger.info(f"Query endpoint accessed - Query: '{request.query}', Language: '{request.language}'")

    user_query = request.query
    language = request.language
   
    try:
        logging.info("Fetching the schema of DB")
        schema = await database_schema()
        
        logging.info("Converting user query to SQL")
        sql_query, llm_error = await query_to_sql(user_query, schema, language)
        if llm_error:
            logger.error(f"LLM error during SQL generation: {llm_error}")
            return {"error": llm_error, "sql": "", "db_result": [], "answer": ""}
        logging.info(f"Generated SQL query: {sql_query}")
        
        logging.info("Executing SQL query")
        db_result = await execute_sql_query(sql_query)
        logger.info(f"SQL query executed successfully, result count: {len(db_result)}")
        
        logging.info("Generating ansewr based on the SQL, Schema & Query")
        answer = await answer_formulation(user_query, db_result, language)

        return {"sql": sql_query, "db_result": db_result, "answer": answer, "error": ""}
    except Exception as e:
        logger.error(f"Error in query endpoint: {str(e)}", exc_info=True)
        return {"error": str(e), "sql": sql_query, "db_result": [], "answer": ""}


# Endpoint to retrieve the database schema
@app.get("/schema")
async def schema_endpoint():
    """Retrieve the database schema"""
    logger.info("Schema endpoint accessed")
    return await database_schema()
