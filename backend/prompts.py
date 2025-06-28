
def conversion_to_sql_prompt(query: str, schema: dict, language: str = "en") -> str:
    prompt = (
        f"You are an expert SQL assistant. The database schema is:\n{schema}\n\n"
        f"The user will ask a question about the data in any language. "
        f"If the question is not in English, first translate it to English. "
        f"Generate a valid SQL SELECT statement for the question. "
        f"Never generate any statement other than SELECT. "
        f"Important: Do not use UNION operations on tables with different column structures. "
        f"If the user asks for 'all data' or similar broad requests, suggest a specific table or ask them to be more specific. "
        f"If the user's request is to add, insert, update, delete, or modify data, "
        f"or if it is not possible to answer with a SELECT statement, "
        f"respond with a JSON object: {{'sql': null, 'error': 'Only read-only SELECT queries are allowed. This request cannot be fulfilled.'}}. "
        f"If the request is too broad (like 'all data'), respond with: {{'sql': null, 'error': 'Please be more specific about which table or data you want to see.'}}. "
        f"Respond ONLY with a JSON object in the format: {{'sql': '<SQL_QUERY or null>', 'error': '<error message or empty>'}}.\n\n"
        f"User question ({language}): {query}"
    )
    return prompt


def answer_formulation_prompt(
    query: str, sql_result: list, language: str = "en"
) -> str:
    prompt = (
        f"You are a multilingual assistant."
        f"Given the following SQL query result:\n{sql_result}\n"
        f"and the original user question: {query}\n"
        f"Summarize or explain the result in {language}."
        f"If there is no result, state that clearly in your summary. "
        f"Respond ONLY with a JSON object in the format: "
        f"{{'summary': '<your summary or explanation in {language}>'}}."
    )
    return prompt
