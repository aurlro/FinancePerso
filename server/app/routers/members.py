"""
Members API Router
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..models import Member
from ..schemas import (
    Member as MemberSchema,
    MemberCreate,
    MemberResponse,
    MemberUpdate,
    SuccessResponse,
)

router = APIRouter()


@router.get("", response_model=list[MemberSchema])
async def list_members(
    db: AsyncSession = Depends(get_db),
):
    """
    List all household members.
    """
    result = await db.execute(
        select(Member).order_by(Member.name)
    )
    members = result.scalars().all()
    return members


@router.post("", response_model=MemberResponse, status_code=status.HTTP_201_CREATED)
async def create_member(
    data: MemberCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new household member.
    """
    member = Member(**data.model_dump())
    db.add(member)
    await db.commit()
    await db.refresh(member)

    return MemberResponse(data=member)


@router.get("/{member_id}", response_model=MemberResponse)
async def get_member(
    member_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Get a single member by ID.
    """
    result = await db.execute(
        select(Member).where(Member.id == member_id)
    )
    member = result.scalar_one_or_none()

    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found",
        )

    return MemberResponse(data=member)


@router.patch("/{member_id}", response_model=MemberResponse)
async def update_member(
    member_id: str,
    data: MemberUpdate,
    db: AsyncSession = Depends(get_db),
):
    """
    Update a member.
    """
    result = await db.execute(
        select(Member).where(Member.id == member_id)
    )
    member = result.scalar_one_or_none()

    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found",
        )

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(member, field, value)

    await db.commit()
    await db.refresh(member)

    return MemberResponse(data=member)


@router.delete("/{member_id}", response_model=SuccessResponse)
async def delete_member(
    member_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Delete a member.
    """
    result = await db.execute(
        select(Member).where(Member.id == member_id)
    )
    member = result.scalar_one_or_none()

    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found",
        )

    await db.delete(member)
    await db.commit()

    return SuccessResponse(message="Member deleted successfully")
