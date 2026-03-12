"""
Households API Router (PR #7)
Handles household management, members, and invitations.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

import secrets
import string
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr

from modules.db.connection import get_db_connection
from modules.logger import logger

from models.schemas import UserResponse
from routers.auth import get_current_user

router = APIRouter(tags=["Households"])


# Pydantic models
class HouseholdCreateRequest(BaseModel):
    name: str
    description: Optional[str] = None


class HouseholdUpdateRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class HouseholdResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    owner_id: int
    created_at: str
    updated_at: str
    member_count: int


class HouseholdMemberResponse(BaseModel):
    id: int
    user_id: int
    name: str
    email: str
    role: str
    is_active: bool
    joined_at: str


class InvitationCreateRequest(BaseModel):
    email: EmailStr
    role: str = "member"  # 'member' or 'admin'


class InvitationResponse(BaseModel):
    id: int
    household_id: int
    email: str
    status: str
    role: str
    expires_at: str
    created_at: str


class AcceptInvitationRequest(BaseModel):
    token: str


def _generate_invitation_token() -> str:
    """Generate a secure invitation token."""
    return ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))


# ============================================
# Household Management
# ============================================

@router.post(
    "",
    response_model=HouseholdResponse,
    summary="Create household",
    description="Create a new household and become the owner.",
    status_code=status.HTTP_201_CREATED,
)
async def create_household(
    request: HouseholdCreateRequest,
    current_user: UserResponse = Depends(get_current_user),
) -> HouseholdResponse:
    """Create a new household."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Check if user already owns a household
            cursor.execute(
                "SELECT id FROM households WHERE owner_id = ?",
                (current_user.id,)
            )
            if cursor.fetchone():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User already owns a household"
                )
            
            # Create household
            now = datetime.now().isoformat()
            cursor.execute(
                """
                INSERT INTO households (name, description, owner_id, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (request.name, request.description, current_user.id, now, now)
            )
            conn.commit()
            household_id = cursor.lastrowid
            
            # Add owner as member
            cursor.execute(
                """
                INSERT INTO household_members (household_id, user_id, role, is_active, joined_at)
                VALUES (?, ?, 'owner', 1, ?)
                """,
                (household_id, current_user.id, now)
            )
            
            # Update user's household_id
            cursor.execute(
                "UPDATE api_users SET household_id = ? WHERE id = ?",
                (household_id, current_user.id)
            )
            conn.commit()
            
            return HouseholdResponse(
                id=household_id,
                name=request.name,
                description=request.description,
                owner_id=current_user.id,
                created_at=now,
                updated_at=now,
                member_count=1,
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating household: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create household: {str(e)}"
        )


@router.get(
    "/my",
    response_model=Optional[HouseholdResponse],
    summary="Get my household",
    description="Get the current user's household.",
)
async def get_my_household(
    current_user: UserResponse = Depends(get_current_user),
) -> Optional[HouseholdResponse]:
    """Get current user's household."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Get household
            cursor.execute(
                """
                SELECT h.*, COUNT(hm.id) as member_count
                FROM households h
                LEFT JOIN household_members hm ON h.id = hm.household_id AND hm.is_active = 1
                WHERE h.id = (SELECT household_id FROM api_users WHERE id = ?)
                GROUP BY h.id
                """,
                (current_user.id,)
            )
            row = cursor.fetchone()
            
            if not row:
                return None
            
            columns = [desc[0] for desc in cursor.description]
            data = dict(zip(columns, row))
            
            return HouseholdResponse(
                id=data["id"],
                name=data["name"],
                description=data.get("description"),
                owner_id=data["owner_id"],
                created_at=data["created_at"],
                updated_at=data["updated_at"],
                member_count=data["member_count"],
            )
            
    except Exception as e:
        logger.error(f"Error getting household: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get household: {str(e)}"
        )


@router.put(
    "/{household_id}",
    response_model=HouseholdResponse,
    summary="Update household",
    description="Update household details (owner only).",
)
async def update_household(
    household_id: int,
    request: HouseholdUpdateRequest,
    current_user: UserResponse = Depends(get_current_user),
) -> HouseholdResponse:
    """Update household."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Check ownership
            cursor.execute(
                "SELECT id FROM households WHERE id = ? AND owner_id = ?",
                (household_id, current_user.id)
            )
            if not cursor.fetchone():
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Only owner can update household"
                )
            
            # Build update
            updates = []
            params = []
            if request.name is not None:
                updates.append("name = ?")
                params.append(request.name)
            if request.description is not None:
                updates.append("description = ?")
                params.append(request.description)
            
            if not updates:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No fields to update"
                )
            
            updates.append("updated_at = ?")
            params.append(datetime.now().isoformat())
            params.append(household_id)
            
            cursor.execute(
                f"UPDATE households SET {', '.join(updates)} WHERE id = ?",
                params
            )
            conn.commit()
            
            # Return updated household
            return await get_my_household(current_user)
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating household: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update household: {str(e)}"
        )


@router.delete(
    "/{household_id}",
    response_model=dict,
    summary="Delete household",
    description="Delete a household (owner only).",
)
async def delete_household(
    household_id: int,
    current_user: UserResponse = Depends(get_current_user),
) -> dict:
    """Delete household."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Check ownership
            cursor.execute(
                "SELECT id FROM households WHERE id = ? AND owner_id = ?",
                (household_id, current_user.id)
            )
            if not cursor.fetchone():
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Only owner can delete household"
                )
            
            # Clear household_id from users
            cursor.execute(
                "UPDATE api_users SET household_id = NULL WHERE household_id = ?",
                (household_id,)
            )
            
            # Delete household (cascade will handle members and invitations)
            cursor.execute(
                "DELETE FROM households WHERE id = ?",
                (household_id,)
            )
            conn.commit()
            
            return {"deleted": True, "id": household_id}
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting household: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete household: {str(e)}"
        )


# ============================================
# Members Management
# ============================================

@router.get(
    "/{household_id}/members",
    response_model=list[HouseholdMemberResponse],
    summary="List members",
    description="Get all members of a household.",
)
async def list_members(
    household_id: int,
    current_user: UserResponse = Depends(get_current_user),
) -> list[HouseholdMemberResponse]:
    """List household members."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Check if user is member
            cursor.execute(
                """
                SELECT 1 FROM household_members 
                WHERE household_id = ? AND user_id = ? AND is_active = 1
                """,
                (household_id, current_user.id)
            )
            if not cursor.fetchone():
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not a member of this household"
                )
            
            # Get members
            cursor.execute(
                """
                SELECT hm.id, hm.user_id, u.name, u.email, hm.role, hm.is_active, hm.joined_at
                FROM household_members hm
                JOIN api_users u ON hm.user_id = u.id
                WHERE hm.household_id = ? AND hm.is_active = 1
                ORDER BY hm.joined_at
                """,
                (household_id,)
            )
            
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            
            members = []
            for row in rows:
                data = dict(zip(columns, row))
                members.append(HouseholdMemberResponse(
                    id=data["id"],
                    user_id=data["user_id"],
                    name=data["name"],
                    email=data["email"],
                    role=data["role"],
                    is_active=bool(data["is_active"]),
                    joined_at=data["joined_at"],
                ))
            
            return members
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing members: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list members: {str(e)}"
        )


@router.delete(
    "/{household_id}/members/{user_id}",
    response_model=dict,
    summary="Remove member",
    description="Remove a member from household (owner/admin only).",
)
async def remove_member(
    household_id: int,
    user_id: int,
    current_user: UserResponse = Depends(get_current_user),
) -> dict:
    """Remove member from household."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Check if current user is owner or admin
            cursor.execute(
                """
                SELECT role FROM household_members 
                WHERE household_id = ? AND user_id = ? AND is_active = 1
                """,
                (household_id, current_user.id)
            )
            row = cursor.fetchone()
            if not row or row[0] not in ('owner', 'admin'):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Only owner or admin can remove members"
                )
            
            # Cannot remove owner
            cursor.execute(
                "SELECT role FROM household_members WHERE household_id = ? AND user_id = ?",
                (household_id, user_id)
            )
            target_row = cursor.fetchone()
            if target_row and target_row[0] == 'owner':
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot remove owner"
                )
            
            # Deactivate member
            cursor.execute(
                """
                UPDATE household_members 
                SET is_active = 0 
                WHERE household_id = ? AND user_id = ?
                """,
                (household_id, user_id)
            )
            
            # Clear household_id from user
            cursor.execute(
                "UPDATE api_users SET household_id = NULL WHERE id = ?",
                (user_id,)
            )
            conn.commit()
            
            return {"removed": True, "user_id": user_id}
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error removing member: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to remove member: {str(e)}"
        )


# ============================================
# Invitations
# ============================================

@router.post(
    "/{household_id}/invitations",
    response_model=InvitationResponse,
    summary="Create invitation",
    description="Invite a user to join the household.",
    status_code=status.HTTP_201_CREATED,
)
async def create_invitation(
    household_id: int,
    request: InvitationCreateRequest,
    current_user: UserResponse = Depends(get_current_user),
) -> InvitationResponse:
    """Create invitation."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Check if current user is owner or admin
            cursor.execute(
                """
                SELECT role FROM household_members 
                WHERE household_id = ? AND user_id = ? AND is_active = 1
                """,
                (household_id, current_user.id)
            )
            row = cursor.fetchone()
            if not row or row[0] not in ('owner', 'admin'):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Only owner or admin can invite"
                )
            
            # Check if email already has pending invitation
            cursor.execute(
                """
                SELECT id FROM household_invitations 
                WHERE household_id = ? AND email = ? AND status = 'pending'
                """,
                (household_id, request.email)
            )
            if cursor.fetchone():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Pending invitation already exists for this email"
                )
            
            # Generate token and create invitation
            token = _generate_invitation_token()
            expires_at = (datetime.now() + timedelta(days=7)).isoformat()
            created_at = datetime.now().isoformat()
            
            cursor.execute(
                """
                INSERT INTO household_invitations 
                (household_id, invited_by, email, token, status, role, expires_at, created_at)
                VALUES (?, ?, ?, ?, 'pending', ?, ?, ?)
                """,
                (household_id, current_user.id, request.email, token, request.role, expires_at, created_at)
            )
            conn.commit()
            invitation_id = cursor.lastrowid
            
            # TODO: Send email with invitation link
            # For now, just return the token
            
            return InvitationResponse(
                id=invitation_id,
                household_id=household_id,
                email=request.email,
                status="pending",
                role=request.role,
                expires_at=expires_at,
                created_at=created_at,
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating invitation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create invitation: {str(e)}"
        )


@router.get(
    "/{household_id}/invitations",
    response_model=list[InvitationResponse],
    summary="List invitations",
    description="Get all pending invitations for a household.",
)
async def list_invitations(
    household_id: int,
    current_user: UserResponse = Depends(get_current_user),
) -> list[InvitationResponse]:
    """List pending invitations."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Check membership
            cursor.execute(
                """
                SELECT 1 FROM household_members 
                WHERE household_id = ? AND user_id = ? AND is_active = 1
                """,
                (household_id, current_user.id)
            )
            if not cursor.fetchone():
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not a member of this household"
                )
            
            cursor.execute(
                """
                SELECT id, household_id, email, status, role, expires_at, created_at
                FROM household_invitations
                WHERE household_id = ? AND status = 'pending'
                ORDER BY created_at DESC
                """,
                (household_id,)
            )
            
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            
            invitations = []
            for row in rows:
                data = dict(zip(columns, row))
                invitations.append(InvitationResponse(**data))
            
            return invitations
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing invitations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list invitations: {str(e)}"
        )


@router.post(
    "/invitations/accept",
    response_model=dict,
    summary="Accept invitation",
    description="Accept a household invitation.",
)
async def accept_invitation(
    request: AcceptInvitationRequest,
    current_user: UserResponse = Depends(get_current_user),
) -> dict:
    """Accept invitation."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Get invitation
            cursor.execute(
                """
                SELECT id, household_id, role, expires_at, status, email
                FROM household_invitations
                WHERE token = ?
                """,
                (request.token,)
            )
            row = cursor.fetchone()
            if not row:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Invitation not found"
                )
            
            invitation_id, household_id, role, expires_at, status, invited_email = row
            
            # Check if expired
            if datetime.now().isoformat() > expires_at:
                cursor.execute(
                    "UPDATE household_invitations SET status = 'expired' WHERE id = ?",
                    (invitation_id,)
                )
                conn.commit()
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invitation has expired"
                )
            
            if status != 'pending':
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invitation is already {status}"
                )
            
            # Check if user is already in a household
            cursor.execute(
                "SELECT household_id FROM api_users WHERE id = ?",
                (current_user.id,)
            )
            user_row = cursor.fetchone()
            if user_row and user_row[0]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User is already in a household"
                )
            
            # Add member
            now = datetime.now().isoformat()
            cursor.execute(
                """
                INSERT INTO household_members (household_id, user_id, role, is_active, joined_at)
                VALUES (?, ?, ?, 1, ?)
                ON CONFLICT(household_id, user_id) DO UPDATE SET
                is_active = 1, role = excluded.role, joined_at = excluded.joined_at
                """,
                (household_id, current_user.id, role, now)
            )
            
            # Update invitation
            cursor.execute(
                """
                UPDATE household_invitations 
                SET status = 'accepted', accepted_at = ?
                WHERE id = ?
                """,
                (now, invitation_id)
            )
            
            # Update user's household_id
            cursor.execute(
                "UPDATE api_users SET household_id = ? WHERE id = ?",
                (household_id, current_user.id)
            )
            conn.commit()
            
            return {"success": True, "household_id": household_id}
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error accepting invitation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to accept invitation: {str(e)}"
        )


@router.post(
    "/invitations/decline",
    response_model=dict,
    summary="Decline invitation",
    description="Decline a household invitation.",
)
async def decline_invitation(
    request: AcceptInvitationRequest,
    current_user: UserResponse = Depends(get_current_user),
) -> dict:
    """Decline invitation."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute(
                """
                UPDATE household_invitations 
                SET status = 'declined'
                WHERE token = ? AND email = ?
                """,
                (request.token, current_user.email)
            )
            conn.commit()
            
            return {"success": True}
            
    except Exception as e:
        logger.error(f"Error declining invitation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to decline invitation: {str(e)}"
        )


@router.delete(
    "/{household_id}/invitations/{invitation_id}",
    response_model=dict,
    summary="Cancel invitation",
    description="Cancel a pending invitation (owner/admin only).",
)
async def cancel_invitation(
    household_id: int,
    invitation_id: int,
    current_user: UserResponse = Depends(get_current_user),
) -> dict:
    """Cancel invitation."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Check permissions
            cursor.execute(
                """
                SELECT role FROM household_members 
                WHERE household_id = ? AND user_id = ? AND is_active = 1
                """,
                (household_id, current_user.id)
            )
            row = cursor.fetchone()
            if not row or row[0] not in ('owner', 'admin'):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Only owner or admin can cancel invitations"
                )
            
            cursor.execute(
                "DELETE FROM household_invitations WHERE id = ? AND household_id = ?",
                (invitation_id, household_id)
            )
            conn.commit()
            
            return {"cancelled": True, "id": invitation_id}
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cancelling invitation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cancel invitation: {str(e)}"
        )
