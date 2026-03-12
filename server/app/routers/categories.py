"""
Categories API Router
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..models import Category
from ..schemas import (
    Category as CategorySchema,
    CategoryCreate,
    CategoryResponse,
    CategoryUpdate,
    SuccessResponse,
)

router = APIRouter()


@router.get("", response_model=list[CategorySchema])
async def list_categories(
    db: AsyncSession = Depends(get_db),
):
    """
    List all categories.
    """
    result = await db.execute(
        select(Category).order_by(Category.name)
    )
    categories = result.scalars().all()
    return categories


@router.post("", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    data: CategoryCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new category.
    """
    # Check for duplicate name
    existing = await db.execute(
        select(Category).where(Category.name == data.name)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Category with this name already exists",
        )

    category = Category(**data.model_dump())
    db.add(category)
    await db.commit()
    await db.refresh(category)

    return CategoryResponse(data=category)


@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(
    category_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Get a single category by ID.
    """
    result = await db.execute(
        select(Category).where(Category.id == category_id)
    )
    category = result.scalar_one_or_none()

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found",
        )

    return CategoryResponse(data=category)


@router.patch("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: str,
    data: CategoryUpdate,
    db: AsyncSession = Depends(get_db),
):
    """
    Update a category.
    """
    result = await db.execute(
        select(Category).where(Category.id == category_id)
    )
    category = result.scalar_one_or_none()

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found",
        )

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(category, field, value)

    await db.commit()
    await db.refresh(category)

    return CategoryResponse(data=category)


@router.delete("/{category_id}", response_model=SuccessResponse)
async def delete_category(
    category_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Delete a category.
    """
    result = await db.execute(
        select(Category).where(Category.id == category_id)
    )
    category = result.scalar_one_or_none()

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found",
        )

    await db.delete(category)
    await db.commit()

    return SuccessResponse(message="Category deleted successfully")
