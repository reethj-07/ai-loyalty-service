from fastapi import APIRouter, HTTPException, status, File, UploadFile, Depends, Query
from pydantic import BaseModel, Field, field_validator
import logging
import csv
import io
from typing import List
# Switched to Supabase repository
from app.repositories.supabase_members_repo import members_repo as sqlite_repo
from app.core.tenant import resolve_tenant_id
from app.services.segmentation_service import get_segmentation_service

router = APIRouter(
    tags=["members"]
)

logger = logging.getLogger(__name__)


@router.get("/{member_id}/rfm")
async def get_member_rfm(member_id: str):
    """
    Returns individual member RFM breakdown with human-readable explanation.
    """
    service = get_segmentation_service()
    return await service.get_member_rfm(member_id)

# Valid membership tiers
VALID_TIERS = {"Bronze", "Silver", "Gold", "Platinum"}


class CreateMemberRequest(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=100, description="Member's first name")
    last_name: str = Field(..., min_length=1, max_length=100, description="Member's last name")
    email: str | None = Field(None, max_length=255, description="Member's email address")
    mobile: str | None = Field(None, max_length=20, description="Member's mobile number")
    tier: str = Field("Bronze", description="Membership tier")

    @field_validator("first_name", "last_name", mode="before")
    @classmethod
    def strip_whitespace(cls, v):
        if isinstance(v, str):
            return v.strip()
        return v

    @field_validator("tier")
    @classmethod
    def validate_tier(cls, v):
        if v not in VALID_TIERS:
            raise ValueError(f"Invalid tier. Must be one of: {', '.join(VALID_TIERS)}")
        return v

    @field_validator("email")
    @classmethod
    def validate_email(cls, v):
        if v is None:
            return v
        if "@" not in v or "." not in v:
            raise ValueError("Invalid email format")
        return v.strip().lower()

    @field_validator("mobile")
    @classmethod
    def validate_mobile(cls, v):
        if v is None:
            return v
        # Allow digits, spaces, hyphens, plus, and parentheses
        import re
        if not re.match(r"^[\d\s\-\+\(\)]+$", v):
            raise ValueError("Invalid mobile format")
        # Ensure at least 10 digits
        if len(re.sub(r"\D", "", v)) < 10:
            raise ValueError("Mobile number must contain at least 10 digits")
        return v.strip()


class TransferPointsRequest(BaseModel):
    from_member: str = Field(..., description="Sender member ID or email")
    to_member: str = Field(..., description="Recipient member ID or email")
    points: int = Field(..., gt=0, description="Points to transfer")


def resolve_member_identifier(identifier: str, tenant_id: str | None = None):
    if "@" in identifier:
        return sqlite_repo.get_member_by_email(identifier, tenant_id=tenant_id)
    return sqlite_repo.get_member_by_id(identifier, tenant_id=tenant_id)


@router.get("")
def list_members(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    search: str | None = Query(None, min_length=1),
    tenant_id: str | None = Depends(resolve_tenant_id),
):
    """
    Get all loyalty program members
    
    Returns:
        - 200: List of members
        - 500: Server error
    """
    try:
        logger.info("Fetching members list")
        members, total = sqlite_repo.list_members(
            limit=limit,
            offset=offset,
            search=search,
            tenant_id=tenant_id,
        )
        
        if members is None:
            members = []
        
        logger.info(f"Successfully fetched {len(members)} members")
        
        return {
            "items": [
                {
                    "id": m.id,
                    "first_name": m.first_name,
                    "last_name": m.last_name,
                    "email": m.email,
                    "mobile": m.mobile,
                    "tier": m.tier,
                    "points_balance": m.points,
                    "status": m.status,
                    "created_at": m.created_at,
                }
                for m in members
            ],
            "total": total,
            "limit": limit,
            "offset": offset,
        }
    except Exception as e:
        logger.error(f"Error fetching members: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch members. Please try again later.",
        )


@router.post("", status_code=status.HTTP_201_CREATED)
def create_member(request: CreateMemberRequest, tenant_id: str | None = Depends(resolve_tenant_id)):
    """
    Create a new loyalty program member
    
    Returns:
        - 201: Successfully created member
        - 400: Invalid input data
        - 500: Server error
    """
    try:
        logger.info(f"Creating member: {request.first_name} {request.last_name}")
        
        member_data = {
            "first_name": request.first_name,
            "last_name": request.last_name,
            "email": request.email,
            "mobile": request.mobile,
            "tier": request.tier,
            "points_balance": 0,
            "status": "active",
        }

        new_member = sqlite_repo.create_member(member_data, tenant_id=tenant_id)

        if not new_member:
            logger.error(f"Failed to create member in database")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create member. Please check your input and try again.",
            )

        logger.info(f"Successfully created member with ID: {new_member.id}")

        return {
            "id": new_member.id,
            "first_name": new_member.first_name,
            "last_name": new_member.last_name,
            "email": new_member.email,
            "mobile": new_member.mobile,
            "tier": new_member.tier,
            "points_balance": new_member.points,
            "status": new_member.status,
            "created_at": new_member.created_at,
        }
    except HTTPException:
        raise
    except ValueError as e:
        logger.warning(f"Validation error creating member: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Validation error: {str(e)}",
        )
    except Exception as e:
        error_str = str(e)
        logger.error(f"Error creating member: {error_str}", exc_info=True)
        
        # Handle duplicate email error from database
        if "duplicate key value violates unique constraint" in error_str and "members_email_key" in error_str:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A member with this email address already exists. Please use a different email.",
            )
        
        # Handle duplicate mobile error
        if "duplicate key value violates unique constraint" in error_str and "members_mobile_key" in error_str:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A member with this mobile number already exists. Please use a different mobile number.",
            )
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred. Please try again later.",
        )


@router.post("/bulk", status_code=status.HTTP_201_CREATED)
async def bulk_create_members(
    file: UploadFile = File(...),
    tenant_id: str | None = Depends(resolve_tenant_id),
):
    """
    Bulk import members from CSV file
    
    CSV Format:
    email,first_name,last_name,mobile,tier
    john@example.com,John,Doe,+1234567890,Gold
    
    Returns:
        - 201: Successfully created members
        - 400: Invalid CSV format
        - 500: Server error
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be a CSV file",
        )
    
    try:
        # Read CSV file
        contents = await file.read()
        decoded = contents.decode('utf-8')
        csv_reader = csv.DictReader(io.StringIO(decoded))
        
        created_count = 0
        failed_count = 0
        error_details = []
        
        for row_num, row in enumerate(csv_reader, start=2):  # Start at 2 (header is row 1)
            try:
                # Extract and validate fields
                member_data = {
                    "first_name": row.get("first_name", "").strip(),
                    "last_name": row.get("last_name", "").strip(),
                    "email": row.get("email", "").strip().lower() or None,
                    "mobile": row.get("mobile", "").strip() or None,
                    "tier": row.get("tier", "Bronze").strip(),
                    "points_balance": int(row.get("points_balance", 0)),
                    "status": row.get("status", "active").strip(),
                }
                
                # Validate required fields
                if not member_data["first_name"]:
                    raise ValueError("first_name is required")
                if not member_data["last_name"]:
                    raise ValueError("last_name is required")
                if member_data["tier"] not in VALID_TIERS:
                    raise ValueError(f"Invalid tier. Must be one of: {', '.join(VALID_TIERS)}")
                
                # Create member
                new_member = sqlite_repo.create_member(member_data, tenant_id=tenant_id)
                if new_member:
                    created_count += 1
                else:
                    failed_count += 1
                    error_details.append(f"Row {row_num}: Failed to create member")
                    
            except Exception as e:
                failed_count += 1
                error_str = str(e)
                if "duplicate key" in error_str:
                    error_details.append(f"Row {row_num}: Duplicate email or mobile")
                else:
                    error_details.append(f"Row {row_num}: {error_str}")
                logger.warning(f"Failed to import row {row_num}: {error_str}")
        
        logger.info(f"Bulk import completed: {created_count} created, {failed_count} failed")
        
        return {
            "status": "completed",
            "created": created_count,
            "failed": failed_count,
            "errors": error_details[:10],  # Return first 10 errors
            "message": f"Successfully imported {created_count} members. {failed_count} failed.",
        }
        
    except Exception as e:
        logger.error(f"Error processing CSV file: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process CSV file: {str(e)}",
        )


@router.put("/{member_id}", status_code=status.HTTP_200_OK)
def update_member(
    member_id: str,
    request: CreateMemberRequest,
    tenant_id: str | None = Depends(resolve_tenant_id)
):
    """
    Update an existing member's information

    Args:
        member_id: Member ID to update
        request: Updated member data
        tenant_id: Optional tenant ID for multi-tenancy

    Returns:
        Updated member object
    """
    try:
        # Check if member exists
        existing_member = sqlite_repo.get_member_by_id(member_id, tenant_id=tenant_id)
        if not existing_member:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Member not found"
            )

        # Update member data
        updated_data = {
            "first_name": request.first_name,
            "last_name": request.last_name,
            "email": request.email,
            "mobile": request.mobile,
            "tier": request.tier,
        }

        updated_member = sqlite_repo.update_member(member_id, updated_data, tenant_id=tenant_id)

        if not updated_member:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update member"
            )

        logger.info(f"Member updated: {member_id}")
        return updated_member

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update member: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update member: {str(e)}"
        )


@router.delete("/{member_id}", status_code=status.HTTP_200_OK)
def delete_member(
    member_id: str,
    tenant_id: str | None = Depends(resolve_tenant_id)
):
    """
    Delete a member from the system

    Args:
        member_id: Member ID to delete
        tenant_id: Optional tenant ID for multi-tenancy

    Returns:
        Success message
    """
    try:
        # Check if member exists
        existing_member = sqlite_repo.get_member_by_id(member_id, tenant_id=tenant_id)
        if not existing_member:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Member not found"
            )

        # Delete member
        deleted = sqlite_repo.delete_member(member_id, tenant_id=tenant_id)

        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete member"
            )

        logger.info(f"Member deleted: {member_id}")
        return {
            "status": "success",
            "message": f"Member {member_id} deleted successfully",
            "member_id": member_id
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete member: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete member: {str(e)}"
        )


@router.post("/points/transfer", status_code=status.HTTP_200_OK)
def transfer_points(request: TransferPointsRequest, tenant_id: str | None = Depends(resolve_tenant_id)):
    try:
        sender = resolve_member_identifier(request.from_member, tenant_id=tenant_id)
        recipient = resolve_member_identifier(request.to_member, tenant_id=tenant_id)

        if not sender or not recipient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Member not found",
            )

        if sender.points < request.points:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Insufficient points balance",
            )

        sender_new_points = sender.points - request.points
        recipient_new_points = recipient.points + request.points

        sender_updated = sqlite_repo.update_member_points(sender.id, sender_new_points, tenant_id=tenant_id)
        recipient_updated = sqlite_repo.update_member_points(recipient.id, recipient_new_points, tenant_id=tenant_id)

        if not sender_updated or not recipient_updated:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update points balance",
            )

        return {
            "status": "success",
            "from_member": sender.id,
            "to_member": recipient.id,
            "points_transferred": request.points,
            "sender_balance": sender_new_points,
            "recipient_balance": recipient_new_points,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Points transfer error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to transfer points",
        )
