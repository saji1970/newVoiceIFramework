from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from server.dependencies import verify_api_key

router = APIRouter(prefix="/connectors", tags=["connectors"])


class ConnectorCreate(BaseModel):
    name: str
    type: str  # http, graphql, db
    config: dict


@router.post("")
async def create_connector(request: ConnectorCreate, _api_key: str = Depends(verify_api_key)):
    """Register a new API connector."""
    raise HTTPException(501, "Connector management not yet implemented")


@router.get("")
async def list_connectors(_api_key: str = Depends(verify_api_key)):
    """List all connectors."""
    return {"connectors": []}


@router.get("/{connector_id}")
async def get_connector(connector_id: str, _api_key: str = Depends(verify_api_key)):
    raise HTTPException(501, "Connector management not yet implemented")


@router.delete("/{connector_id}")
async def delete_connector(connector_id: str, _api_key: str = Depends(verify_api_key)):
    raise HTTPException(501, "Connector management not yet implemented")


@router.post("/{connector_id}/test")
async def test_connector(connector_id: str, _api_key: str = Depends(verify_api_key)):
    """Test a connector's connectivity."""
    raise HTTPException(501, "Connector management not yet implemented")
