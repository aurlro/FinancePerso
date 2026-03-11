"""
Rules API Router
Handles CRUD operations for categorization rules.
"""

import sys
from pathlib import Path
# Add FinancePerso root to path for importing modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from fastapi import APIRouter, Depends, HTTPException, status

from modules.db.connection import get_db_connection
from modules.db.rules import (
    add_learning_rule,
    delete_learning_rule,
    get_learning_rules,
    update_learning_rule,
)
from modules.db.transactions import get_all_transactions
from modules.logger import logger

from models.schemas import (
    RuleCreateRequest,
    RuleResponse,
    RuleUpdateRequest,
    RulesListResponse,
    RuleTestRequest,
    RuleTestResponse,
)

from routers.auth import get_current_user, UserResponse

import re

router = APIRouter(tags=["Rules"])


def _compile_pattern(pattern: str) -> re.Pattern | None:
    """Compile a pattern for matching, supporting wildcards."""
    try:
        # Convert simple wildcard pattern to regex
        if "*" in pattern or "?" in pattern:
            regex_pattern = pattern.replace("*", ".*").replace("?", ".")
        else:
            # Default: partial match (contains)
            regex_pattern = f".*{re.escape(pattern)}.*"
        
        return re.compile(regex_pattern, re.IGNORECASE)
    except re.error:
        return None


@router.get(
    "",
    response_model=RulesListResponse,
    summary="List rules",
    description="Get all categorization rules.",
    responses={
        500: {"description": "Internal server error"},
    },
)
async def list_rules(
    current_user: UserResponse = Depends(get_current_user),
) -> RulesListResponse:
    """
    Get all categorization rules.

    Returns:
        RulesListResponse with all rules
    """
    try:
        df = get_learning_rules()
        
        items = []
        for _, row in df.iterrows():
            items.append(RuleResponse(
                id=int(row["id"]),
                pattern=row["pattern"],
                category=row["category"],
                priority=int(row.get("priority", 1)),
                created_at=row.get("created_at", ""),
                match_count=None,  # Could be calculated if needed
            ))

        logger.info(f"Listed {len(items)} rules")
        return RulesListResponse(items=items, total=len(items))

    except Exception as e:
        logger.error(f"Error listing rules: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve rules: {str(e)}",
        )


@router.post(
    "",
    response_model=RuleResponse,
    summary="Create rule",
    description="Create a new categorization rule.",
    responses={
        400: {"description": "Rule already exists"},
        500: {"description": "Internal server error"},
    },
)
async def create_rule(
    request: RuleCreateRequest,
    current_user: UserResponse = Depends(get_current_user),
) -> RuleResponse:
    """
    Create a new categorization rule.

    Args:
        request: Rule creation data
        current_user: The authenticated user

    Returns:
        Created rule
    """
    try:
        success = add_learning_rule(request.pattern, request.category, request.priority)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to create rule with pattern '{request.pattern}'",
            )

        # Get the created rule (get_learning_rules is cached, need to clear or use fresh query)
        with get_db_connection() as conn:
            import pandas as pd
            df = pd.read_sql(
                "SELECT * FROM learning_rules WHERE pattern = ? ORDER BY created_at DESC LIMIT 1",
                conn,
                params=(request.pattern,)
            )
        
        if df.empty:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Rule created but could not be retrieved",
            )
        
        created = df.iloc[0]

        logger.info(f"Created rule: {request.pattern} -> {request.category}")
        return RuleResponse(
            id=int(created["id"]),
            pattern=created["pattern"],
            category=created["category"],
            priority=int(created.get("priority", 1)),
            created_at=created.get("created_at", ""),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating rule: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create rule: {str(e)}",
        )


@router.put(
    "/{rule_id}",
    response_model=RuleResponse,
    summary="Update rule",
    description="Update a rule by ID.",
    responses={
        404: {"description": "Rule not found"},
        500: {"description": "Internal server error"},
    },
)
async def update_rule(
    rule_id: int,
    request: RuleUpdateRequest,
    current_user: UserResponse = Depends(get_current_user),
) -> RuleResponse:
    """
    Update a categorization rule.

    Args:
        rule_id: Rule ID to update
        request: Update data
        current_user: The authenticated user

    Returns:
        Updated rule
    """
    try:
        # Check if rule exists
        df = get_learning_rules()
        rule_row = df[df["id"] == rule_id]
        
        if rule_row.empty:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Rule with ID {rule_id} not found",
            )

        # Apply updates using existing function
        update_learning_rule(
            rule_id=rule_id,
            new_pattern=request.pattern,
            new_category=request.category,
            new_priority=request.priority,
        )

        # Get updated rule
        df = get_learning_rules()
        updated = df[df["id"] == rule_id].iloc[0]

        logger.info(f"Updated rule: {rule_id}")
        return RuleResponse(
            id=int(updated["id"]),
            pattern=updated["pattern"],
            category=updated["category"],
            priority=int(updated.get("priority", 1)),
            created_at=updated.get("created_at", ""),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating rule {rule_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update rule: {str(e)}",
        )


@router.delete(
    "/{rule_id}",
    response_model=dict,
    summary="Delete rule",
    description="Delete a rule by ID.",
    responses={
        404: {"description": "Rule not found"},
        500: {"description": "Internal server error"},
    },
)
async def delete_rule_endpoint(
    rule_id: int,
    current_user: UserResponse = Depends(get_current_user),
) -> dict:
    """
    Delete a categorization rule.

    Args:
        rule_id: Rule ID to delete
        current_user: The authenticated user

    Returns:
        Deletion confirmation
    """
    try:
        success = delete_learning_rule(rule_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Rule with ID {rule_id} not found",
            )

        logger.info(f"Deleted rule: {rule_id}")
        return {"deleted": True, "id": rule_id}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting rule {rule_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete rule: {str(e)}",
        )


@router.post(
    "/test",
    response_model=RuleTestResponse,
    summary="Test rule pattern",
    description="Test a rule pattern against transaction labels.",
    responses={
        500: {"description": "Internal server error"},
    },
)
async def test_rule(
    request: RuleTestRequest,
    current_user: UserResponse = Depends(get_current_user),
) -> RuleTestResponse:
    """
    Test a rule pattern against transaction labels.

    Args:
        request: Test request with pattern and optional labels
        current_user: The authenticated user

    Returns:
        RuleTestResponse with match results
    """
    try:
        # Get test labels
        if request.test_labels:
            test_labels = request.test_labels
        else:
            # Use recent transaction labels from database
            df = get_all_transactions()
            if len(df) > 0:
                test_labels = df["label"].dropna().unique().tolist()[:100]  # Limit to 100
            else:
                test_labels = []

        # Compile pattern
        pattern = _compile_pattern(request.pattern)
        
        if pattern is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid pattern: '{request.pattern}'",
            )

        # Find matches
        matches = [label for label in test_labels if pattern.search(str(label))]

        logger.info(f"Tested pattern '{request.pattern}': {len(matches)} matches")
        return RuleTestResponse(
            pattern=request.pattern,
            matches=matches,
            match_count=len(matches),
            total_tested=len(test_labels),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error testing rule pattern: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to test rule pattern: {str(e)}",
        )
