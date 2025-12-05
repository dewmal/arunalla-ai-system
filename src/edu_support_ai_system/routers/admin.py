"""Admin API router for agent configuration management"""

from typing import Optional
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, Field

from ..auth import admin_api_key_header, get_admin_api_key_from_header
from ..services.agent_manager import agent_manager
from ..database_models import AgentConfig, AgentPromptHistory

router = APIRouter(prefix="/admin", tags=["admin"])


# Request/Response Models
class AgentConfigRequest(BaseModel):
    """Request model for creating/updating agent configuration"""

    model: str = Field(
        ..., description="Model identifier (e.g., google::gemini-2.5-flash)"
    )
    system_prompt: str = Field(..., description="System prompt for the agent")
    temperature: Optional[float] = Field(
        0.7, ge=0.0, le=2.0, description="Model temperature"
    )
    max_tokens: Optional[int] = Field(2048, gt=0, description="Maximum tokens")
    enabled: bool = Field(True, description="Whether the agent is enabled")
    config_metadata: Optional[dict] = Field(
        None, description="Additional configuration metadata"
    )
    change_reason: Optional[str] = Field(None, description="Reason for the change")


class AgentConfigResponse(BaseModel):
    """Response model for agent configuration"""

    name: str
    model: str
    system_prompt: str
    temperature: Optional[float]
    max_tokens: Optional[int]
    enabled: bool
    config_metadata: Optional[dict]
    created_at: Optional[str]
    updated_at: Optional[str]
    updated_by: Optional[str]

    class Config:
        from_attributes = True


class AgentPromptHistoryResponse(BaseModel):
    """Response model for agent prompt history"""

    id: int
    agent_name: str
    old_prompt: Optional[str]
    new_prompt: str
    changed_at: str
    changed_by: Optional[str]
    change_reason: Optional[str]

    class Config:
        from_attributes = True


class MessageResponse(BaseModel):
    """Generic message response"""

    message: str
    success: bool = True


@router.get("/agents", response_model=list[AgentConfigResponse])
async def list_agents(
    enabled_only: bool = False, _: str = Depends(get_admin_api_key_from_header)
):
    """
    List all agent configurations

    Args:
        enabled_only: If True, only return enabled agents

    Returns:
        List of agent configurations
    """
    configs = agent_manager.list_agent_configs(enabled_only=enabled_only)

    return [
        AgentConfigResponse(
            name=c.name,
            model=c.model,
            system_prompt=c.system_prompt,
            temperature=c.temperature,
            max_tokens=c.max_tokens,
            enabled=c.enabled,
            config_metadata=c.config_metadata,
            created_at=c.created_at.isoformat() if c.created_at else None,
            updated_at=c.updated_at.isoformat() if c.updated_at else None,
            updated_by=c.updated_by,
        )
        for c in configs
    ]


@router.get("/agents/{agent_name}", response_model=AgentConfigResponse)
async def get_agent(agent_name: str, _: str = Depends(get_admin_api_key_from_header)):
    """
    Get specific agent configuration

    Args:
        agent_name: Name of the agent

    Returns:
        Agent configuration

    Raises:
        HTTPException: If agent not found
    """
    config = agent_manager.get_agent_config(agent_name)

    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent '{agent_name}' not found",
        )

    return AgentConfigResponse(
        name=config.name,
        model=config.model,
        system_prompt=config.system_prompt,
        temperature=config.temperature,
        max_tokens=config.max_tokens,
        enabled=config.enabled,
        config_metadata=config.config_metadata,
        created_at=config.created_at.isoformat() if config.created_at else None,
        updated_at=config.updated_at.isoformat() if config.updated_at else None,
        updated_by=config.updated_by,
    )


@router.post(
    "/agents/{agent_name}",
    response_model=AgentConfigResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_agent(
    agent_name: str,
    request: AgentConfigRequest,
    admin_key: str = Depends(get_admin_api_key_from_header),
):
    """
    Create a new agent configuration

    Args:
        agent_name: Name of the agent
        request: Agent configuration data

    Returns:
        Created agent configuration

    Raises:
        HTTPException: If agent already exists
    """
    # Check if agent already exists
    existing = agent_manager.get_agent_config(agent_name)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Agent '{agent_name}' already exists",
        )

    config = agent_manager.create_agent_config(
        name=agent_name,
        model=request.model,
        system_prompt=request.system_prompt,
        temperature=request.temperature,
        max_tokens=request.max_tokens,
        enabled=request.enabled,
        config_metadata=request.config_metadata,
        created_by="admin",
    )

    if not config:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create agent configuration",
        )

    return AgentConfigResponse(
        name=config.name,
        model=config.model,
        system_prompt=config.system_prompt,
        temperature=config.temperature,
        max_tokens=config.max_tokens,
        enabled=config.enabled,
        config_metadata=config.config_metadata,
        created_at=config.created_at.isoformat() if config.created_at else None,
        updated_at=config.updated_at.isoformat() if config.updated_at else None,
        updated_by=config.updated_by,
    )


@router.put("/agents/{agent_name}", response_model=AgentConfigResponse)
async def update_agent(
    agent_name: str,
    request: AgentConfigRequest,
    admin_key: str = Depends(get_admin_api_key_from_header),
):
    """
    Update an existing agent configuration

    Args:
        agent_name: Name of the agent
        request: Updated agent configuration data

    Returns:
        Updated agent configuration

    Raises:
        HTTPException: If agent not found
    """
    config = agent_manager.update_agent_config(
        name=agent_name,
        model=request.model,
        system_prompt=request.system_prompt,
        temperature=request.temperature,
        max_tokens=request.max_tokens,
        enabled=request.enabled,
        config_metadata=request.config_metadata,
        updated_by="admin",
        change_reason=request.change_reason,
    )

    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent '{agent_name}' not found",
        )

    return AgentConfigResponse(
        name=config.name,
        model=config.model,
        system_prompt=config.system_prompt,
        temperature=config.temperature,
        max_tokens=config.max_tokens,
        enabled=config.enabled,
        config_metadata=config.config_metadata,
        created_at=config.created_at.isoformat() if config.created_at else None,
        updated_at=config.updated_at.isoformat() if config.updated_at else None,
        updated_by=config.updated_by,
    )


@router.delete("/agents/{agent_name}", response_model=MessageResponse)
async def delete_agent(
    agent_name: str, _: str = Depends(get_admin_api_key_from_header)
):
    """
    Delete an agent configuration

    Args:
        agent_name: Name of the agent

    Returns:
        Success message

    Raises:
        HTTPException: If agent not found
    """
    success = agent_manager.delete_agent_config(agent_name)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent '{agent_name}' not found",
        )

    return MessageResponse(
        message=f"Agent '{agent_name}' deleted successfully", success=True
    )


@router.get(
    "/agents/{agent_name}/history", response_model=list[AgentPromptHistoryResponse]
)
async def get_agent_history(
    agent_name: str, limit: int = 50, _: str = Depends(get_admin_api_key_from_header)
):
    """
    Get prompt change history for an agent

    Args:
        agent_name: Name of the agent
        limit: Maximum number of history entries to return

    Returns:
        List of prompt history entries
    """
    history = agent_manager.get_prompt_history(agent_name, limit=limit)

    return [
        AgentPromptHistoryResponse(
            id=h.id,
            agent_name=h.agent_name,
            old_prompt=h.old_prompt,
            new_prompt=h.new_prompt,
            changed_at=h.changed_at.isoformat(),
            changed_by=h.changed_by,
            change_reason=h.change_reason,
        )
        for h in history
    ]


@router.post("/agents/{agent_name}/reload", response_model=MessageResponse)
async def reload_agent(
    agent_name: str, _: str = Depends(get_admin_api_key_from_header)
):
    """
    Reload an agent with its current configuration

    Args:
        agent_name: Name of the agent

    Returns:
        Success message

    Note:
        This endpoint is a placeholder for future implementation
        of hot-reloading agent instances
    """
    config = agent_manager.get_agent_config(agent_name)

    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent '{agent_name}' not found",
        )

    # TODO: Implement actual agent reloading logic
    # For now, just clear the cache
    if agent_name in agent_manager._agent_cache:
        del agent_manager._agent_cache[agent_name]

    return MessageResponse(
        message=f"Agent '{agent_name}' will be reloaded on next request", success=True
    )
