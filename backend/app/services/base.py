# backend/app/services/base.py
import time
import logging
# abc removed: concrete base class for flexible composition
from typing import Any, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.config import settings

logger = logging.getLogger("neuroplan.services")

class BaseService:
    """
    Senior-level Service Blueprint.
    Wraps all operations with performance tracking, logging, and audit capability.
    Mirroring the BaseAgent pattern from the AMA2 project.
    """
    def __init__(self, db: AsyncSession = None, name: str = "base_service"):
        self.db = db
        self.name = name

    def _log_decision(self, session_id: UUID, decision_key: str, value: Any, rationale: str):
        """
        Record a decision into the system log.
        In Phase 2, this will also write to the AgentDecisionORM table for a full audit trail.
        """
        logger.info(
            f"[{self.name}] Decision: {decision_key} = {value} | Rationale: {rationale}",
            extra={"session_id": str(session_id), "decision_key": decision_key}
        )

    async def execute_with_trace(self, session_id: UUID, *args, **kwargs) -> Any:
        """
        Template method that wraps execution with instrumentation.
        """
        start_time = time.perf_counter()
        logger.info(f"Starting {self.name} for session {session_id}")
        
        try:
            result = await self._run(session_id, *args, **kwargs)
            duration = time.perf_counter() - start_time
            logger.info(f"Completed {self.name} in {duration:.4f}s")
            return result
        except Exception as e:
            logger.error(f"Error in {self.name}: {str(e)}", exc_info=True)
            raise

    async def _run(self, session_id: UUID, *args, **kwargs) -> Any:
        """Subclasses can override this for instrumented execution via execute_with_trace()."""
        raise NotImplementedError(f"{self.name} has not implemented _run()")
