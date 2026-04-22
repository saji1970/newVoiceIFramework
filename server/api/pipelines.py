from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from server.dependencies import verify_api_key
from server.model_server.config_loader import PipelineConfig, parse_pipeline_dict
from server.model_server.pipeline import PipelineExecutionError, pipeline_engine

router = APIRouter(prefix="/pipelines", tags=["pipelines"])

# In-memory pipeline store (backed by DB in production)
_pipelines: dict[str, dict] = {}


class PipelineCreate(BaseModel):
    name: str
    description: str | None = None
    config: dict
    version: str = "1.0"


class PipelineResponse(BaseModel):
    id: str
    name: str
    description: str | None
    config: dict
    version: str
    enabled: bool


class PipelineRunRequest(BaseModel):
    input: dict
    variables: dict | None = None


@router.post("", response_model=PipelineResponse)
async def create_pipeline(
    request: PipelineCreate,
    _api_key: str = Depends(verify_api_key),
):
    """Create a new pipeline from config."""
    # Validate the pipeline config
    try:
        parsed = parse_pipeline_dict(request.config)
    except Exception as e:
        raise HTTPException(400, f"Invalid pipeline config: {e}")

    errors = pipeline_engine.validate(parsed)
    if errors:
        raise HTTPException(400, f"Pipeline validation errors: {errors}")

    pid = uuid.uuid4().hex
    _pipelines[pid] = {
        "id": pid,
        "name": request.name,
        "description": request.description,
        "config": request.config,
        "version": request.version,
        "enabled": True,
        "parsed": parsed,
    }

    return PipelineResponse(
        id=pid,
        name=request.name,
        description=request.description,
        config=request.config,
        version=request.version,
        enabled=True,
    )


@router.get("")
async def list_pipelines(_api_key: str = Depends(verify_api_key)):
    """List all pipelines."""
    return {
        "pipelines": [
            {
                "id": p["id"],
                "name": p["name"],
                "description": p["description"],
                "version": p["version"],
                "enabled": p["enabled"],
            }
            for p in _pipelines.values()
        ]
    }


@router.get("/{pipeline_id}")
async def get_pipeline(pipeline_id: str, _api_key: str = Depends(verify_api_key)):
    """Get pipeline by ID."""
    p = _pipelines.get(pipeline_id)
    if not p:
        raise HTTPException(404, "Pipeline not found")
    return PipelineResponse(
        id=p["id"],
        name=p["name"],
        description=p["description"],
        config=p["config"],
        version=p["version"],
        enabled=p["enabled"],
    )


@router.put("/{pipeline_id}")
async def update_pipeline(
    pipeline_id: str,
    request: PipelineCreate,
    _api_key: str = Depends(verify_api_key),
):
    """Update a pipeline."""
    if pipeline_id not in _pipelines:
        raise HTTPException(404, "Pipeline not found")

    try:
        parsed = parse_pipeline_dict(request.config)
    except Exception as e:
        raise HTTPException(400, f"Invalid pipeline config: {e}")

    _pipelines[pipeline_id].update(
        {
            "name": request.name,
            "description": request.description,
            "config": request.config,
            "version": request.version,
            "parsed": parsed,
        }
    )

    return PipelineResponse(
        id=pipeline_id,
        name=request.name,
        description=request.description,
        config=request.config,
        version=request.version,
        enabled=_pipelines[pipeline_id]["enabled"],
    )


@router.delete("/{pipeline_id}")
async def delete_pipeline(pipeline_id: str, _api_key: str = Depends(verify_api_key)):
    """Delete a pipeline."""
    if pipeline_id not in _pipelines:
        raise HTTPException(404, "Pipeline not found")
    del _pipelines[pipeline_id]
    return {"status": "deleted"}


@router.post("/{pipeline_id}/run")
async def run_pipeline(
    pipeline_id: str,
    request: PipelineRunRequest,
    _api_key: str = Depends(verify_api_key),
):
    """Execute a pipeline."""
    p = _pipelines.get(pipeline_id)
    if not p:
        raise HTTPException(404, "Pipeline not found")
    if not p.get("enabled"):
        raise HTTPException(400, "Pipeline is disabled")

    parsed: PipelineConfig = p["parsed"]
    try:
        result = await pipeline_engine.execute(
            config=parsed,
            input_data=request.input,
            variables=request.variables,
        )
        return result
    except PipelineExecutionError as e:
        raise HTTPException(500, f"Pipeline execution failed at node '{e.node_id}': {e}")
    except Exception as e:
        raise HTTPException(500, f"Pipeline execution failed: {e}")


@router.post("/validate")
async def validate_pipeline(
    config: dict,
    _api_key: str = Depends(verify_api_key),
):
    """Validate a pipeline config without saving it."""
    try:
        parsed = parse_pipeline_dict(config)
        errors = pipeline_engine.validate(parsed)
        return {"valid": len(errors) == 0, "errors": errors}
    except Exception as e:
        return {"valid": False, "errors": [str(e)]}
