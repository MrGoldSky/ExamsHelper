import asyncio
from typing import Dict, Optional, Any
from datetime import datetime, timedelta
from utils.logger import botLogger


class AnswerWaiterService:
    def __init__(self) -> None:
        self._pendingFutures: Dict[int, asyncio.Future[str]] = {}
        self._examSessions: Dict[int, Dict[str, Any]] = {}

    def createFutureForUser(self, userId: int) -> asyncio.Future[str]:
        future = asyncio.Future()
        if userId in self._pendingFutures:
            oldFuture = self._pendingFutures[userId]
            if not oldFuture.done():
                oldFuture.cancel()
        self._pendingFutures[userId] = future
        return future

    def getFutureResult(self, userId: int) -> Optional[asyncio.Future[str]]:
        return self._pendingFutures.get(userId)

    def setAnswer(self, userId: int, answer: str) -> bool:
        future = self.getFutureResult(userId)
        if future and not future.done():
            future.set_result(answer)
            return True
        return False

    def hasPendingAnswer(self, userId: int) -> bool:
        return userId in self._pendingFutures

    def removeFuture(self, userId: int) -> None:
        if userId in self._pendingFutures:
            future = self._pendingFutures[userId]
            if not future.done():
                future.cancel()
            del self._pendingFutures[userId]

    async def waitForAnswer(
        self,
        userId: int,
        timeLimit: int,
        timeEnabled: bool,
        examStartTime: Optional[datetime] = None
    ) -> Optional[str]:
        future = self.getFutureResult(userId)
        if not future:
            return None

        try:
            if timeEnabled:
                if examStartTime:
                    elapsed = datetime.now() - examStartTime
                    remaining = timedelta(minutes=timeLimit) - elapsed
                    timeoutSeconds = max(0, remaining.total_seconds())
                else:
                    timeoutSeconds = timeLimit * 60

                if timeoutSeconds <= 0:
                    return None

                result = await asyncio.wait_for(future, timeout=timeoutSeconds)
            else:
                result = await future

            return result
        except asyncio.TimeoutError:
            botLogger.warning(f"Timeout waiting for answer from user {userId}")
            return None
        except Exception as e:
            botLogger.error(f"Error waiting for answer: {e}")
            return None
        finally:
            self.removeFuture(userId)

    def createExamSession(self, userId: int, sessionData: Dict[str, Any]) -> None:
        self._examSessions[userId] = sessionData

    def getExamSession(self, userId: int) -> Optional[Dict[str, Any]]:
        return self._examSessions.get(userId)

    def removeExamSession(self, userId: int) -> None:
        if userId in self._examSessions:
            del self._examSessions[userId]
        self.removeFuture(userId)
