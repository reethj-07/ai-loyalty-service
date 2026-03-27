from fastapi import APIRouter, HTTPException, status, File, UploadFile, Depends
from pydantic import BaseModel, Field
import logging
import csv
import io
from datetime import datetime, timezone
# Switched to Supabase repository
from app.repositories.supabase_transactions_repo import transactions_repo
from app.repositories.supabase_members_repo import members_repo
from app.core.event_queue import event_queue
from app.schemas.events import TransactionEvent, IngestionMetadata
from app.core.tenant import resolve_tenant_id

router = APIRouter(tags=["transactions"])

logger = logging.getLogger(__name__)


def resolve_member_id(member_id: str, tenant_id: str | None = None) -> str:
    """
    Resolve a member identifier. If an email is provided, look up the member ID.
    """
    if "@" in member_id:
        member = members_repo.get_member_by_email(member_id, tenant_id=tenant_id)
        if not member:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Member email not found. Please create the member first.",
            )
        return member.id
    return member_id


class CreateTransactionRequest(BaseModel):
    member_id: str = Field(..., description="Member ID or email")
    amount: float = Field(..., description="Transaction amount")
    merchant: str = Field(default="Unknown", description="Merchant name")
    type: str = Field(default="purchase", description="Transaction type")
    category: str = Field(default="general", description="Transaction category")


@router.get("")
def list_transactions(tenant_id: str | None = Depends(resolve_tenant_id)):
    txns = transactions_repo.list_recent(tenant_id=tenant_id)
    return [
        {
            "id": t.id,
            "timestamp": t.created_at,
            "member_id": t.member_id,
            "merchant": t.merchant or "Unknown",
            "type": t.type,
            "amount": t.amount,
        }
        for t in txns
    ]


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_transaction(
    request: CreateTransactionRequest,
    tenant_id: str | None = Depends(resolve_tenant_id),
):
    """
    Create a new transaction
    
    Returns:
        - 201: Successfully created transaction
        - 400: Invalid input data
        - 500: Server error
    """
    try:
        resolved_member_id = resolve_member_id(request.member_id, tenant_id=tenant_id)
        txn_data = {
            "member_id": resolved_member_id,
            "amount": request.amount,
            "merchant": request.merchant,
            "type": request.type,
            "category": request.category,
            "transaction_date": datetime.now(timezone.utc).isoformat(),
        }
        
        new_txn = transactions_repo.create_transaction(txn_data, tenant_id=tenant_id)
        
        if not new_txn:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create transaction",
            )
        
        await event_queue.publish({
            "member_id": resolved_member_id,
            "payload": TransactionEvent(
                transaction_id=new_txn.id,
                member_id=resolved_member_id,
                amount=new_txn.amount,
                currency=new_txn.currency or "USD",
                merchant=new_txn.merchant or "Unknown",
                category=request.category,
                channel="api",
                transaction_date=datetime.now(timezone.utc),
                metadata=IngestionMetadata(
                    tenant_id=tenant_id or "default",
                    source="transactions_api",
                ),
            ),
        })

        return {
            "id": new_txn.id,
            "timestamp": new_txn.created_at,
            "member_id": new_txn.member_id,
            "merchant": new_txn.merchant,
            "type": new_txn.type,
            "amount": new_txn.amount,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating transaction: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )


@router.post("/bulk", status_code=status.HTTP_201_CREATED)
async def bulk_create_transactions(
    file: UploadFile = File(...),
    tenant_id: str | None = Depends(resolve_tenant_id),
):
    """
    Bulk import transactions from CSV file
    
    CSV Format:
    member_id,amount,merchant,type,category
    test@example.com,250.00,Nike Store,purchase,retail
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be a CSV file",
        )
    
    try:
        contents = await file.read()
        decoded = contents.decode('utf-8')
        csv_reader = csv.DictReader(io.StringIO(decoded))
        
        created_count = 0
        failed_count = 0
        
        for row in csv_reader:
            try:
                raw_member_id = row.get("member_id", "").strip()
                resolved_member_id = resolve_member_id(raw_member_id, tenant_id=tenant_id)
                txn_data = {
                    "member_id": resolved_member_id,
                    "amount": float(row.get("amount", 0)),
                    "merchant": row.get("merchant", "Unknown").strip(),
                    "type": row.get("type", "purchase").strip(),
                    "category": row.get("category", "general").strip(),
                    "transaction_date": datetime.now(timezone.utc).isoformat(),
                }
                
                new_txn = transactions_repo.create_transaction(txn_data, tenant_id=tenant_id)
                if new_txn:
                    created_count += 1
                    await event_queue.publish({
                        "member_id": resolved_member_id,
                        "payload": TransactionEvent(
                            transaction_id=new_txn.id,
                            member_id=resolved_member_id,
                            amount=new_txn.amount,
                            currency=new_txn.currency or "USD",
                            merchant=new_txn.merchant or "Unknown",
                            category=txn_data.get("category", "general"),
                            channel="bulk_csv",
                            transaction_date=datetime.now(timezone.utc),
                            metadata=IngestionMetadata(
                                tenant_id=tenant_id or "default",
                                source="transactions_csv",
                            ),
                        ),
                    })
                else:
                    failed_count += 1
            except Exception as e:
                failed_count += 1
                logger.warning(f"Failed to import transaction: {str(e)}")
        
        return {
            "status": "completed",
            "created": created_count,
            "failed": failed_count,
            "message": f"Successfully imported {created_count} transactions. {failed_count} failed.",
        }
    except Exception as e:
        logger.error(f"Error processing CSV file: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process CSV file: {str(e)}",
        )