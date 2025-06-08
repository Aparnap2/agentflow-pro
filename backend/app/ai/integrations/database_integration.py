"""
Database Integration Module

Provides database connectivity and operations for agents.
"""

import logging
from typing import Any, Dict, List, Optional, Union
import json
import pandas as pd
from pydantic import BaseModel, Field, validator
import sqlalchemy
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger(__name__)

class DatabaseConfig(BaseModel):
    """Configuration for database connection."""
    connection_string: str
    pool_size: int = 5
    max_overflow: int = 10
    pool_timeout: int = 30
    pool_recycle: int = 3600
    echo: bool = False
    connect_args: Dict[str, Any] = Field(default_factory=dict)

class QueryResult(BaseModel):
    """Result of a database query."""
    success: bool
    data: Optional[List[Dict[str, Any]]] = None
    columns: Optional[List[str]] = None
    rowcount: int = 0
    error: Optional[str] = None
    execution_time: Optional[float] = None
    sql: Optional[str] = None

class DatabaseIntegration:
    """
    Handles database connections and operations.
    
    This class provides a high-level interface for database operations,
    including executing queries, managing transactions, and handling connections.
    """
    
    def __init__(self, config: Union[Dict[str, Any], DatabaseConfig]):
        """
        Initialize the database integration.
        
        Args:
            config: Database configuration as a dict or DatabaseConfig instance
        """
        if isinstance(config, dict):
            self.config = DatabaseConfig(**config)
        else:
            self.config = config
            
        self.engine = None
        self.session_factory = None
        self._initialize_engine()
    
    def _initialize_engine(self) -> None:
        """Initialize the SQLAlchemy engine and session factory."""
        try:
            self.engine = create_engine(
                self.config.connection_string,
                pool_size=self.config.pool_size,
                max_overflow=self.config.max_overflow,
                pool_timeout=self.config.pool_timeout,
                pool_recycle=self.config.pool_recycle,
                echo=self.config.echo,
                **self.config.connect_args
            )
            
            self.session_factory = scoped_session(
                sessionmaker(
                    autocommit=False,
                    autoflush=False,
                    bind=self.engine
                )
            )
            
            logger.info("Database engine initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize database engine: {str(e)}")
            raise
    
    def get_session(self):
        """Get a new database session."""
        if not self.session_factory:
            self._initialize_engine()
        return self.session_factory()
    
    async def execute_query(
        self,
        query: str,
        params: Optional[Dict[str, Any]] = None,
        fetch: bool = True
    ) -> QueryResult:
        """
        Execute a SQL query.
        
        Args:
            query: SQL query string
            params: Parameters for the query
            fetch: Whether to fetch results
            
        Returns:
            QueryResult with the query results
        """
        import time
        start_time = time.time()
        session = self.get_session()
        
        try:
            result = session.execute(text(query), params or {})
            
            if fetch:
                # For SELECT queries
                if result.returns_rows:
                    columns = list(result.keys())
                    data = [dict(zip(columns, row)) for row in result.fetchall()]
                    return QueryResult(
                        success=True,
                        data=data,
                        columns=columns,
                        rowcount=len(data),
                        execution_time=time.time() - start_time,
                        sql=query
                    )
                # For INSERT/UPDATE/DELETE
                else:
                    session.commit()
                    return QueryResult(
                        success=True,
                        rowcount=result.rowcount,
                        execution_time=time.time() - start_time,
                        sql=query
                    )
            else:
                session.commit()
                return QueryResult(
                    success=True,
                    execution_time=time.time() - start_time,
                    sql=query
                )
                
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Query failed: {str(e)}")
            return QueryResult(
                success=False,
                error=str(e),
                execution_time=time.time() - start_time,
                sql=query
            )
            
        except Exception as e:
            session.rollback()
            logger.error(f"Unexpected error executing query: {str(e)}", exc_info=True)
            return QueryResult(
                success=False,
                error=f"Unexpected error: {str(e)}",
                execution_time=time.time() - start_time,
                sql=query
            )
            
        finally:
            session.close()
    
    async def execute_many(
        self,
        query: str,
        params_list: List[Dict[str, Any]]
    ) -> QueryResult:
        """
        Execute a query multiple times with different parameter sets.
        
        Args:
            query: SQL query string
            params_list: List of parameter dictionaries
            
        Returns:
            QueryResult with the execution status
        """
        import time
        start_time = time.time()
        session = self.get_session()
        
        try:
            result = session.execute(text(query), params_list)
            session.commit()
            
            return QueryResult(
                success=True,
                rowcount=result.rowcount,
                execution_time=time.time() - start_time,
                sql=query
            )
            
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Bulk execute failed: {str(e)}")
            return QueryResult(
                success=False,
                error=str(e),
                execution_time=time.time() - start_time,
                sql=query
            )
            
        finally:
            session.close()
    
    async def execute_pandas_query(
        self,
        query: str,
        params: Optional[Dict[str, Any]] = None
    ) -> pd.DataFrame:
        """
        Execute a query and return results as a pandas DataFrame.
        
        Args:
            query: SQL query string
            params: Parameters for the query
            
        Returns:
            DataFrame with query results
            
        Raises:
            Exception: If the query fails
        """
        try:
            with self.engine.connect() as connection:
                return pd.read_sql_query(query, connection, params=params)
                
        except Exception as e:
            logger.error(f"Pandas query failed: {str(e)}")
            raise
    
    async def table_exists(self, table_name: str, schema: Optional[str] = None) -> bool:
        """
        Check if a table exists in the database.
        
        Args:
            table_name: Name of the table
            schema: Optional schema name
            
        Returns:
            bool: True if the table exists, False otherwise
        """
        query = """
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = COALESCE(:schema, current_schema())
            AND table_name = :table_name
        )
        """
        
        result = await self.execute_query(
            query,
            params={"schema": schema, "table_name": table_name}
        )
        
        return result.success and result.data[0]["exists"] if result.data else False
    
    async def get_table_schema(self, table_name: str, schema: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get the schema of a table.
        
        Args:
            table_name: Name of the table
            schema: Optional schema name
            
        Returns:
            List of column definitions
        """
        query = """
        SELECT 
            column_name,
            data_type,
            is_nullable,
            column_default,
            character_maximum_length,
            numeric_precision,
            numeric_scale
        FROM information_schema.columns
        WHERE table_schema = COALESCE(:schema, current_schema())
        AND table_name = :table_name
        ORDER BY ordinal_position
        """
        
        result = await self.execute_query(
            query,
            params={"schema": schema, "table_name": table_name}
        )
        
        return result.data if result.success else []
    
    async def close(self) -> None:
        """Close all database connections."""
        if self.engine:
            self.engine.dispose()
            logger.info("Database connections closed")

# Example usage
if __name__ == "__main__":
    import asyncio
    from dotenv import load_dotenv
    import os
    
    load_dotenv()
    
    async def test_database():
        # Example configuration
        config = {
            "connection_string": os.getenv("DATABASE_URL", "sqlite:///:memory:"),
            "pool_size": 5,
            "max_overflow": 10,
            "echo": True
        }
        
        db = DatabaseIntegration(config)
        
        # Test query
        result = await db.execute_query("SELECT 1 as test")
        print(f"Test query result: {result.data}")
        
        # Test table operations
        table_name = "test_table"
        if not await db.table_exists(table_name):
            create_sql = f"""
            CREATE TABLE {table_name} (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100),
                value INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
            await db.execute_query(create_sql, fetch=False)
            print(f"Created table {table_name}")
        
        # Insert data
        insert_sql = f"""
        INSERT INTO {table_name} (name, value) 
        VALUES (:name, :value)
        RETURNING id, name, value, created_at
        """
        
        insert_result = await db.execute_query(
            insert_sql,
            params={"name": "test", "value": 42}
        )
        
        if insert_result.success:
            print(f"Inserted record: {insert_result.data}")
        
        # Query data
        select_result = await db.execute_query(
            f"SELECT * FROM {table_name}"
        )
        
        if select_result.success:
            print(f"Selected {select_result.rowcount} rows:")
            for row in select_result.data:
                print(f"  - {row}")
        
        # Test pandas integration
        try:
            df = await db.execute_pandas_query(f"SELECT * FROM {table_name}")
            print("\nPandas DataFrame:")
            print(df)
        except ImportError:
            print("Pandas not available")
        
        # Clean up
        await db.execute_query(f"DROP TABLE IF EXISTS {table_name}", fetch=False)
        await db.close()
    
    asyncio.run(test_database())
