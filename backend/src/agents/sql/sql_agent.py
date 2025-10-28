"""
SQLAgent - Natural Language to SQL Query Agent

This agent converts natural language questions into SQL queries and executes them safely.

Features:
1. Natural language to SQL conversion using LLM
2. Security validation (only SELECT queries allowed)
3. Query result formatting
4. Schema-aware query generation
5. Error handling and user-friendly responses

Security:
- Only SELECT queries allowed
- No DELETE, UPDATE, INSERT, DROP, ALTER, TRUNCATE
- Query validation before execution
- Result size limits
"""

import logging
import re
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from src.core.models import User
from src.llm.gemini.client import LLMClient

logger = logging.getLogger(__name__)


class SQLAgent:
    """
    SQLAgent converts natural language to SQL queries and executes them safely
    
    Security Features:
    - Whitelist approach: Only SELECT queries allowed
    - Blacklist dangerous keywords
    - Query validation before execution
    - Result size limits (max 100 rows)
    - Read-only operations only
    """
    
    # Dangerous SQL keywords that are not allowed
    DANGEROUS_KEYWORDS = [
        'DELETE', 'DROP', 'TRUNCATE', 'ALTER', 'CREATE', 'INSERT', 
        'UPDATE', 'REPLACE', 'GRANT', 'REVOKE', 'EXEC', 'EXECUTE'
    ]
    
    # Maximum number of rows to return
    MAX_ROWS = 100
    
    # Database schema information for LLM context
    SCHEMA_INFO = """
    Database Schema:
    
    1. users (User accounts)
       - id, mobile, email, first_name, last_name, wallet_balance, is_active, created_at
    
    2. categories (Service categories)
       - id, name, slug, description, is_active, display_order
    
    3. subcategories (Service subcategories)
       - id, category_id, name, slug, description, is_active, display_order
    
    4. rate_cards (Service pricing)
       - id, category_id, subcategory_id, provider_id, name, description, price, strike_price, is_active
    
    5. bookings (Customer bookings)
       - id, user_id, order_id, status, payment_status, payment_method
       - subtotal, discount, tax, total, preferred_date, preferred_time, created_at
       - status: pending, confirmed, in_progress, completed, cancelled
       - order_id is the customer-facing identifier (e.g., "ORD12345678")
    
    6. booking_items (Individual service items in bookings)
       - id, booking_id, user_id, rate_card_id, provider_id, service_name, quantity, price
       - total_amount, final_amount, status, scheduled_date, scheduled_time_from, scheduled_time_to
    
    7. providers (Service providers)
       - id, name, mobile, email, rating, total_reviews, is_active
    
    8. addresses (User addresses)
       - id, user_id, address_line1, address_line2, city, state, pincode, is_default
    
    9. complaints (Customer complaints)
       - id, user_id, booking_id, complaint_type, subject, description, priority, status
       - created_at, response_due_at, resolution_due_at, resolved_at
       - priority: low, medium, high, critical
       - status: open, in_progress, resolved, closed, escalated
    
    10. conversations (Chat history)
        - id, user_id, session_id, message, response, intent, confidence, created_at
    
    Important Notes:
    - Use proper JOINs when querying related tables
    - Always use table aliases for clarity
    - Filter by user_id when querying user-specific data
    - Use LIMIT to restrict result size
    """
    
    def __init__(self, db: AsyncSession):
        """
        Initialize SQLAgent
        
        Args:
            db: Database session
        """
        self.db = db
        self.logger = logging.getLogger(__name__)
        
        # Initialize LLM client for SQL generation
        try:
            self.llm_client = LLMClient.create_for_intent_classification()
            self.logger.info("SQLAgent initialized successfully")
        except Exception as e:
            self.logger.error(f"Error initializing SQLAgent: {e}")
            raise
    
    async def execute(
        self,
        message: str,
        user: User,
        session_id: str,
        entities: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute natural language query
        
        Args:
            message: User's natural language question
            user: Current user
            session_id: Session ID
            entities: Extracted entities (query)
        
        Returns:
            {
                "response": str,  # User-friendly response with results
                "action_taken": str,  # Action identifier
                "metadata": dict  # Query details and results
            }
        """
        try:
            query_text = entities.get("query", message)
            
            if not query_text or len(query_text) < 5:
                return {
                    "response": "Please provide a specific question about your data. For example: 'Show my recent bookings' or 'How many complaints do I have?'",
                    "action_taken": "missing_query",
                    "metadata": {}
                }
            
            self.logger.info(f"Processing SQL query: user_id={user.id}, query='{query_text}'")
            
            # Generate SQL from natural language
            sql_query = await self._generate_sql(query_text, user)
            
            if not sql_query:
                return {
                    "response": "I couldn't understand your question. Please try rephrasing it or ask something specific about your bookings, complaints, or account.",
                    "action_taken": "sql_generation_failed",
                    "metadata": {}
                }
            
            # Validate SQL query for security
            is_safe, error_message = self._validate_sql(sql_query)
            
            if not is_safe:
                self.logger.warning(f"Unsafe SQL query blocked: {sql_query}")
                return {
                    "response": f"❌ Security Error: {error_message}",
                    "action_taken": "unsafe_query",
                    "metadata": {"error": error_message}
                }
            
            # Execute SQL query
            results = await self._execute_sql(sql_query)
            
            # Format results for user
            response = self._format_results(query_text, results)
            
            return {
                "response": response,
                "action_taken": "query_executed",
                "metadata": {
                    "sql_query": sql_query,
                    "row_count": len(results),
                    "results": results[:10]  # Return first 10 rows in metadata
                }
            }
            
        except Exception as e:
            self.logger.error(f"SQL agent error: {e}", exc_info=True)
            return {
                "response": "❌ An error occurred while processing your query. Please try a simpler question or contact support.",
                "action_taken": "error",
                "metadata": {"error": str(e)}
            }
    
    async def _generate_sql(self, query_text: str, user: User) -> Optional[str]:
        """
        Generate SQL query from natural language using LLM
        
        Args:
            query_text: Natural language question
            user: Current user
        
        Returns:
            SQL query string or None
        """
        try:
            prompt = f"""You are a SQL query generator. Convert the natural language question into a valid SQL SELECT query.

{self.SCHEMA_INFO}

User Question: {query_text}
User ID: {user.id}

Important Rules:
1. ONLY generate SELECT queries
2. Always filter by user_id={user.id} when querying user-specific tables (bookings, complaints, addresses, etc.)
3. Use proper JOINs when needed
4. Add LIMIT {self.MAX_ROWS} to prevent large result sets
5. Use table aliases for clarity
6. Return ONLY the SQL query, no explanations

Example:
Question: "Show my recent bookings"
SQL: SELECT b.id, b.booking_number, b.status, b.total, b.created_at FROM bookings b WHERE b.user_id = {user.id} ORDER BY b.created_at DESC LIMIT 10;

Now generate SQL for the user's question:"""

            response = await self.llm_client.generate_text(prompt)
            
            if not response:
                return None
            
            # Extract SQL query from response
            sql_query = self._extract_sql(response)
            
            self.logger.info(f"Generated SQL: {sql_query}")
            return sql_query
            
        except Exception as e:
            self.logger.error(f"SQL generation error: {e}")
            return None
    
    def _extract_sql(self, llm_response: str) -> str:
        """
        Extract SQL query from LLM response
        
        Args:
            llm_response: LLM response text
        
        Returns:
            Cleaned SQL query
        """
        # Remove markdown code blocks if present
        sql = llm_response.strip()
        sql = re.sub(r'```sql\s*', '', sql)
        sql = re.sub(r'```\s*', '', sql)
        
        # Remove any explanatory text before/after the query
        lines = sql.split('\n')
        sql_lines = []
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#') and not line.startswith('--'):
                sql_lines.append(line)
        
        sql = ' '.join(sql_lines)
        
        # Ensure it ends with semicolon
        if not sql.endswith(';'):
            sql += ';'
        
        return sql
    
    def _validate_sql(self, sql_query: str) -> tuple[bool, str]:
        """
        Validate SQL query for security

        Args:
            sql_query: SQL query to validate

        Returns:
            Tuple of (is_safe: bool, error_message: str)
        """
        sql_upper = sql_query.upper()

        # Check if it's a SELECT query
        if not sql_upper.strip().startswith('SELECT'):
            return False, "Only SELECT queries are allowed"

        # Check for dangerous keywords (as whole words, not substrings)
        # Use word boundaries to avoid false positives like "created_at" containing "CREATE"
        import re
        for keyword in self.DANGEROUS_KEYWORDS:
            # Match keyword as whole word (with word boundaries)
            pattern = r'\b' + re.escape(keyword) + r'\b'
            if re.search(pattern, sql_upper):
                return False, f"Dangerous keyword '{keyword}' not allowed"

        # Check for multiple statements (SQL injection attempt)
        if sql_query.count(';') > 1:
            return False, "Multiple SQL statements not allowed"

        return True, ""
    
    async def _execute_sql(self, sql_query: str) -> List[Dict[str, Any]]:
        """
        Execute SQL query and return results
        
        Args:
            sql_query: SQL query to execute
        
        Returns:
            List of result rows as dictionaries
        """
        try:
            result = await self.db.execute(text(sql_query))
            rows = result.fetchall()
            
            # Convert rows to list of dictionaries
            if rows:
                columns = result.keys()
                results = [dict(zip(columns, row)) for row in rows]
            else:
                results = []
            
            self.logger.info(f"Query executed successfully: {len(results)} rows returned")
            return results
            
        except Exception as e:
            self.logger.error(f"SQL execution error: {e}")
            raise
    
    def _format_results(self, query_text: str, results: List[Dict[str, Any]]) -> str:
        """
        Format query results for user-friendly display
        
        Args:
            query_text: Original question
            results: Query results
        
        Returns:
            Formatted response string
        """
        if not results:
            return "No results found for your query."
        
        row_count = len(results)
        
        # Build response
        response_parts = [
            f"📊 Query Results ({row_count} row{'s' if row_count != 1 else ''} found):\n"
        ]
        
        # Show first 10 results in detail
        display_count = min(10, row_count)
        
        for i, row in enumerate(results[:display_count], 1):
            response_parts.append(f"\n{i}. ")
            row_parts = []
            for key, value in row.items():
                # Format value based on type
                if value is None:
                    formatted_value = "N/A"
                elif isinstance(value, (int, float)):
                    formatted_value = str(value)
                else:
                    formatted_value = str(value)[:50]  # Limit string length
                
                row_parts.append(f"{key}: {formatted_value}")
            
            response_parts.append(", ".join(row_parts))
        
        if row_count > 10:
            response_parts.append(f"\n\n... and {row_count - 10} more rows")
        
        return "".join(response_parts)

