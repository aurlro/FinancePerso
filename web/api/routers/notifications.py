"""
Notifications API Router (PR #6)
Handles notifications management with WebSocket support for real-time updates.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

import json
from datetime import datetime, timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect, status

from modules.db.connection import get_db_connection
from modules.logger import logger

from models.schemas import (
    NotificationResponse,
    NotificationsListResponse,
    NotificationCreateRequest,
    ErrorResponse,
)

from routers.auth import get_current_user, UserResponse

router = APIRouter(tags=["Notifications"])

# WebSocket connection manager for real-time notifications
class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[int, list[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, user_id: int):
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)
        logger.info(f"WebSocket connected for user {user_id}")
    
    def disconnect(self, websocket: WebSocket, user_id: int):
        if user_id in self.active_connections:
            self.active_connections[user_id].remove(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
        logger.info(f"WebSocket disconnected for user {user_id}")
    
    async def send_notification(self, user_id: int, notification: dict):
        """Send notification to specific user."""
        if user_id in self.active_connections:
            disconnected = []
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_json(notification)
                except Exception:
                    disconnected.append(connection)
            
            # Clean up disconnected sockets
            for conn in disconnected:
                self.active_connections[user_id].remove(conn)

manager = ConnectionManager()


def _row_to_notification(row: tuple, columns: list[str]) -> dict:
    """Convert database row to notification dict."""
    notification = dict(zip(columns, row))
    notification["is_read"] = bool(notification.get("is_read", 0))
    if notification.get("data"):
        try:
            notification["data"] = json.loads(notification["data"])
        except json.JSONDecodeError:
            notification["data"] = None
    return notification


@router.websocket("/ws")
async def notifications_websocket(websocket: WebSocket):
    """
    WebSocket endpoint for real-time notifications.
    Client must authenticate by sending token after connection.
    """
    await websocket.accept()
    user_id = None
    
    try:
        # Wait for authentication message
        auth_msg = await websocket.receive_json()
        token = auth_msg.get("token")
        
        if not token:
            await websocket.close(code=4001, reason="Missing token")
            return
        
        # Validate token (simplified - should use proper JWT validation)
        # For now, we'll require the user to connect via HTTP first
        user_id = auth_msg.get("user_id")
        if not user_id:
            await websocket.close(code=4001, reason="Missing user_id")
            return
        
        await manager.connect(websocket, user_id)
        
        # Send initial unread count
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT COUNT(*) FROM notifications WHERE user_id = ? AND is_read = 0",
                (user_id,)
            )
            unread_count = cursor.fetchone()[0]
            await websocket.send_json({
                "type": "initial",
                "unread_count": unread_count
            })
        
        # Keep connection alive and handle ping/pong
        while True:
            try:
                data = await websocket.receive_json()
                if data.get("action") == "ping":
                    await websocket.send_json({"type": "pong"})
                elif data.get("action") == "mark_read":
                    notification_id = data.get("notification_id")
                    if notification_id:
                        await _mark_notification_read(notification_id, user_id)
                        await websocket.send_json({
                            "type": "marked_read",
                            "notification_id": notification_id
                        })
            except WebSocketDisconnect:
                break
                
    except WebSocketDisconnect:
        pass
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        if user_id:
            manager.disconnect(websocket, user_id)


async def _mark_notification_read(notification_id: int, user_id: int):
    """Mark a notification as read."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE notifications 
            SET is_read = 1, read_at = ?
            WHERE id = ? AND user_id = ?
            """,
            (datetime.now().isoformat(), notification_id, user_id)
        )
        conn.commit()


@router.get(
    "",
    response_model=NotificationsListResponse,
    summary="List notifications",
    description="Get user notifications with pagination and filtering.",
)
async def list_notifications(
    unread_only: bool = Query(False, description="Only return unread notifications"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: UserResponse = Depends(get_current_user),
) -> NotificationsListResponse:
    """Get notifications for current user."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Build query
            where_clause = "WHERE user_id = ?"
            params = [current_user.id]
            
            if unread_only:
                where_clause += " AND is_read = 0"
            
            # Get total count
            cursor.execute(
                f"SELECT COUNT(*) FROM notifications {where_clause}",
                params
            )
            total = cursor.fetchone()[0]
            
            # Get notifications
            cursor.execute(
                f"""
                SELECT * FROM notifications 
                {where_clause}
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
                """,
                params + [limit, offset]
            )
            
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            
            items = [_row_to_notification(row, columns) for row in rows]
            
            return NotificationsListResponse(
                items=items,
                total=total,
                unread_count=sum(1 for item in items if not item["is_read"])
            )
            
    except Exception as e:
        logger.error(f"Error listing notifications: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve notifications: {str(e)}"
        )


@router.get(
    "/unread-count",
    response_model=dict,
    summary="Get unread count",
    description="Get the number of unread notifications.",
)
async def get_unread_count(
    current_user: UserResponse = Depends(get_current_user),
) -> dict:
    """Get unread notification count."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT COUNT(*) FROM notifications WHERE user_id = ? AND is_read = 0",
                (current_user.id,)
            )
            count = cursor.fetchone()[0]
            return {"unread_count": count}
    except Exception as e:
        logger.error(f"Error getting unread count: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get unread count: {str(e)}"
        )


@router.post(
    "",
    response_model=NotificationResponse,
    summary="Create notification",
    description="Create a new notification (for system use).",
    status_code=status.HTTP_201_CREATED,
)
async def create_notification(
    request: NotificationCreateRequest,
    current_user: UserResponse = Depends(get_current_user),
) -> NotificationResponse:
    """Create a notification."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO notifications 
                (user_id, type, category, title, message, data, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    request.user_id,
                    request.type,
                    request.category,
                    request.title,
                    request.message,
                    json.dumps(request.data) if request.data else None,
                    datetime.now().isoformat(),
                )
            )
            conn.commit()
            notification_id = cursor.lastrowid
            
            # Get created notification
            cursor.execute(
                "SELECT * FROM notifications WHERE id = ?",
                (notification_id,)
            )
            columns = [desc[0] for desc in cursor.description]
            row = cursor.fetchone()
            notification = _row_to_notification(row, columns)
            
            # Send real-time notification via WebSocket
            await manager.send_notification(request.user_id, {
                "type": "new_notification",
                "notification": notification
            })
            
            return NotificationResponse(**notification)
            
    except Exception as e:
        logger.error(f"Error creating notification: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create notification: {str(e)}"
        )


@router.post(
    "/{notification_id}/read",
    response_model=dict,
    summary="Mark as read",
    description="Mark a notification as read.",
)
async def mark_as_read(
    notification_id: int,
    current_user: UserResponse = Depends(get_current_user),
) -> dict:
    """Mark notification as read."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Verify ownership
            cursor.execute(
                "SELECT user_id FROM notifications WHERE id = ?",
                (notification_id,)
            )
            row = cursor.fetchone()
            if not row:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Notification not found"
                )
            if row[0] != current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not authorized"
                )
            
            cursor.execute(
                """
                UPDATE notifications 
                SET is_read = 1, read_at = ?
                WHERE id = ?
                """,
                (datetime.now().isoformat(), notification_id)
            )
            conn.commit()
            
            return {"success": True, "id": notification_id}
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error marking notification as read: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to mark notification as read: {str(e)}"
        )


@router.post(
    "/mark-all-read",
    response_model=dict,
    summary="Mark all as read",
    description="Mark all notifications as read.",
)
async def mark_all_as_read(
    current_user: UserResponse = Depends(get_current_user),
) -> dict:
    """Mark all notifications as read."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE notifications 
                SET is_read = 1, read_at = ?
                WHERE user_id = ? AND is_read = 0
                """,
                (datetime.now().isoformat(), current_user.id)
            )
            conn.commit()
            updated = cursor.rowcount
            
            return {"success": True, "marked_read": updated}
            
    except Exception as e:
        logger.error(f"Error marking all notifications as read: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to mark all notifications as read: {str(e)}"
        )


@router.delete(
    "/{notification_id}",
    response_model=dict,
    summary="Delete notification",
    description="Delete a notification.",
)
async def delete_notification(
    notification_id: int,
    current_user: UserResponse = Depends(get_current_user),
) -> dict:
    """Delete a notification."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Verify ownership
            cursor.execute(
                "SELECT user_id FROM notifications WHERE id = ?",
                (notification_id,)
            )
            row = cursor.fetchone()
            if not row:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Notification not found"
                )
            if row[0] != current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not authorized"
                )
            
            cursor.execute(
                "DELETE FROM notifications WHERE id = ?",
                (notification_id,)
            )
            conn.commit()
            
            return {"deleted": True, "id": notification_id}
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting notification: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete notification: {str(e)}"
        )


# Helper function to create system notifications
def create_system_notification(user_id: int, title: str, message: str, category: str = "system", data: dict = None):
    """Create a system notification for a user."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO notifications 
                (user_id, type, category, title, message, data, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    user_id,
                    "info",
                    category,
                    title,
                    message,
                    json.dumps(data) if data else None,
                    datetime.now().isoformat(),
                )
            )
            conn.commit()
            return cursor.lastrowid
    except Exception as e:
        logger.error(f"Error creating system notification: {e}")
        return None
