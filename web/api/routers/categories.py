"""
Categories API Router
Handles CRUD operations for transaction categories.
"""

import sys
from pathlib import Path
# Add FinancePerso root to path for importing modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from fastapi import APIRouter, Depends, HTTPException, status

from modules.db.categories import (
    add_category,
    delete_category,
    update_category_emoji,
    update_category_fixed,
    update_category_suggested_tags,
)
from modules.db.connection import get_db_connection
from modules.logger import logger

from models.schemas import (
    CategoryCreateRequest,
    CategoryResponse,
    CategoryUpdateRequest,
    CategoriesListResponse,
    ErrorResponse,
)

from routers.auth import get_current_user, UserResponse

router = APIRouter(tags=["Categories"])


@router.get(
    "",
    response_model=CategoriesListResponse,
    summary="List categories",
    description="Get all transaction categories.",
    responses={
        500: {"description": "Internal server error"},
    },
)
async def list_categories(
    current_user: UserResponse = Depends(get_current_user),
) -> CategoriesListResponse:
    """
    Get all categories.

    Returns:
        CategoriesListResponse with all categories
    """
    try:
        # Bypass cache for fresh data
        with get_db_connection() as conn:
            import pandas as pd
            df = pd.read_sql("SELECT * FROM categories ORDER BY name", conn)
        
        items = []
        for _, row in df.iterrows():
            items.append(CategoryResponse(
                id=int(row["id"]),
                name=row["name"],
                emoji=row.get("emoji", "🏷️"),
                is_fixed=row.get("is_fixed", 0),
                suggested_tags=row.get("suggested_tags"),
                created_at=row.get("created_at", ""),
            ))

        logger.info(f"Listed {len(items)} categories")
        return CategoriesListResponse(items=items, total=len(items))

    except Exception as e:
        logger.error(f"Error listing categories: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve categories: {str(e)}",
        )


@router.post(
    "",
    response_model=CategoryResponse,
    summary="Create category",
    description="Create a new transaction category.",
    responses={
        400: {"description": "Category already exists"},
        500: {"description": "Internal server error"},
    },
)
async def create_category(
    request: CategoryCreateRequest,
    current_user: UserResponse = Depends(get_current_user),
) -> CategoryResponse:
    """
    Create a new category.

    Args:
        request: Category creation data
        current_user: The authenticated user

    Returns:
        Created category
    """
    try:
        success = add_category(
            name=request.name,
            emoji=request.emoji,
            is_fixed=request.is_fixed,
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Category '{request.name}' already exists",
            )

        # Get the created category (bypass cache)
        with get_db_connection() as conn:
            import pandas as pd
            df = pd.read_sql(
                "SELECT * FROM categories WHERE name = ?",
                conn,
                params=(request.name,)
            )
        created = df.iloc[0].to_dict()

        logger.info(f"Created category: {request.name}")
        return CategoryResponse(
            id=int(created["id"]),
            name=created["name"],
            emoji=created.get("emoji", "🏷️"),
            is_fixed=created.get("is_fixed", 0),
            suggested_tags=created.get("suggested_tags"),
            created_at=created.get("created_at", ""),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating category: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create category: {str(e)}",
        )


@router.put(
    "/{category_id}",
    response_model=CategoryResponse,
    summary="Update category",
    description="Update a category by ID.",
    responses={
        404: {"description": "Category not found"},
        500: {"description": "Internal server error"},
    },
)
async def update_category(
    category_id: int,
    request: CategoryUpdateRequest,
    current_user: UserResponse = Depends(get_current_user),
) -> CategoryResponse:
    """
    Update a category.

    Args:
        category_id: Category ID to update
        request: Update data
        current_user: The authenticated user

    Returns:
        Updated category
    """
    try:
        # Find category by ID (bypass cache)
        with get_db_connection() as conn:
            import pandas as pd
            df = pd.read_sql("SELECT * FROM categories WHERE id = ?", conn, params=(category_id,))
        
        if df.empty:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category with ID {category_id} not found",
            )

        # Apply updates
        if request.emoji is not None:
            update_category_emoji(category_id, request.emoji)
        if request.is_fixed is not None:
            update_category_fixed(category_id, request.is_fixed)
        if request.suggested_tags is not None:
            update_category_suggested_tags(category_id, request.suggested_tags)

        # Get updated category (bypass cache)
        with get_db_connection() as conn:
            import pandas as pd
            df = pd.read_sql(
                "SELECT * FROM categories WHERE id = ?",
                conn,
                params=(category_id,)
            )
        updated = df.iloc[0].to_dict()

        logger.info(f"Updated category: {category_id}")
        return CategoryResponse(
            id=int(updated["id"]),
            name=updated["name"],
            emoji=updated.get("emoji", "🏷️"),
            is_fixed=updated.get("is_fixed", 0),
            suggested_tags=updated.get("suggested_tags"),
            created_at=updated.get("created_at", ""),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating category {category_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update category: {str(e)}",
        )


@router.delete(
    "/{category_id}",
    response_model=dict,
    summary="Delete category",
    description="Delete a category by ID.",
    responses={
        404: {"description": "Category not found"},
        500: {"description": "Internal server error"},
    },
)
async def delete_category_endpoint(
    category_id: int,
    current_user: UserResponse = Depends(get_current_user),
) -> dict:
    """
    Delete a category.

    Args:
        category_id: Category ID to delete
        current_user: The authenticated user

    Returns:
        Deletion confirmation
    """
    try:
        # Check if category exists (bypass cache)
        with get_db_connection() as conn:
            import pandas as pd
            df = pd.read_sql("SELECT * FROM categories WHERE id = ?", conn, params=(category_id,))
        
        if df.empty:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category with ID {category_id} not found",
            )

        delete_category(category_id)

        logger.info(f"Deleted category: {category_id}")
        return {"deleted": True, "id": category_id}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting category {category_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete category: {str(e)}",
        )
