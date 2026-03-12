"""
Members API Router
Handles CRUD operations for household members.
"""

import sys
from pathlib import Path
# Add FinancePerso root to path for importing modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from fastapi import APIRouter, Depends, HTTPException, status

from modules.db.members import (
    add_member,
    delete_member,
    get_members,
    update_member_type,
)
from modules.logger import logger

from models.schemas import (
    MemberCreateRequest,
    MemberResponse,
    MemberUpdateRequest,
    MembersListResponse,
)

from routers.auth import get_current_user, UserResponse

router = APIRouter(tags=["Members"])


@router.get(
    "",
    response_model=MembersListResponse,
    summary="List members",
    description="Get all household members.",
    responses={
        500: {"description": "Internal server error"},
    },
)
async def list_members(
    current_user: UserResponse = Depends(get_current_user),
) -> MembersListResponse:
    """
    Get all members.

    Returns:
        MembersListResponse with all members
    """
    try:
        df = get_members()
        
        items = []
        for _, row in df.iterrows():
            items.append(MemberResponse(
                id=int(row["id"]),
                name=row["name"],
                member_type=row.get("member_type", "HOUSEHOLD"),
                created_at=row.get("created_at", ""),
            ))

        logger.info(f"Listed {len(items)} members")
        return MembersListResponse(items=items, total=len(items))

    except Exception as e:
        logger.error(f"Error listing members: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve members: {str(e)}",
        )


@router.post(
    "",
    response_model=MemberResponse,
    summary="Create member",
    description="Create a new household member.",
    responses={
        400: {"description": "Member already exists"},
        500: {"description": "Internal server error"},
    },
)
async def create_member(
    request: MemberCreateRequest,
    current_user: UserResponse = Depends(get_current_user),
) -> MemberResponse:
    """
    Create a new member.

    Args:
        request: Member creation data
        current_user: The authenticated user

    Returns:
        Created member
    """
    try:
        success = add_member(request.name, request.member_type)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Member '{request.name}' already exists",
            )

        # Get the created member
        df = get_members()
        created = df[df["name"] == request.name].iloc[0]

        logger.info(f"Created member: {request.name}")
        return MemberResponse(
            id=int(created["id"]),
            name=created["name"],
            member_type=created.get("member_type", "HOUSEHOLD"),
            created_at=created.get("created_at", ""),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating member: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create member: {str(e)}",
        )


@router.put(
    "/{member_id}",
    response_model=MemberResponse,
    summary="Update member",
    description="Update a member by ID.",
    responses={
        404: {"description": "Member not found"},
        500: {"description": "Internal server error"},
    },
)
async def update_member(
    member_id: int,
    request: MemberUpdateRequest,
    current_user: UserResponse = Depends(get_current_user),
) -> MemberResponse:
    """
    Update a member.

    Args:
        member_id: Member ID to update
        request: Update data
        current_user: The authenticated user

    Returns:
        Updated member
    """
    try:
        # Check if member exists
        df = get_members()
        member_row = df[df["id"] == member_id]
        
        if member_row.empty:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Member with ID {member_id} not found",
            )

        # Apply updates
        if request.member_type is not None:
            update_member_type(member_id, request.member_type)

        # Get updated member
        df = get_members()
        updated = df[df["id"] == member_id].iloc[0]

        logger.info(f"Updated member: {member_id}")
        return MemberResponse(
            id=int(updated["id"]),
            name=updated["name"],
            member_type=updated.get("member_type", "HOUSEHOLD"),
            created_at=updated.get("created_at", ""),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating member {member_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update member: {str(e)}",
        )


@router.delete(
    "/{member_id}",
    response_model=dict,
    summary="Delete member",
    description="Delete a member by ID.",
    responses={
        404: {"description": "Member not found"},
        500: {"description": "Internal server error"},
    },
)
async def delete_member_endpoint(
    member_id: int,
    current_user: UserResponse = Depends(get_current_user),
) -> dict:
    """
    Delete a member.

    Args:
        member_id: Member ID to delete
        current_user: The authenticated user

    Returns:
        Deletion confirmation
    """
    try:
        # Check if member exists
        df = get_members()
        member_row = df[df["id"] == member_id]
        
        if member_row.empty:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Member with ID {member_id} not found",
            )

        delete_member(member_id)

        logger.info(f"Deleted member: {member_id}")
        return {"deleted": True, "id": member_id}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting member {member_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete member: {str(e)}",
        )
