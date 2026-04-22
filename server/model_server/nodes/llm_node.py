from __future__ import annotations

from typing import Any

from server.model_server.nodes.base import PipelineNode, NodeResult, PipelineContext
from server.providers.registry import provider_registry


class LLMNode(PipelineNode):
    """Node that calls an LLM provider."""

    node_type = "llm"

    async def execute(self, inputs: dict[str, Any], context: PipelineContext) -> NodeResult:
        provider_name = self.config.get("provider", "openai")
        model = self.config.get("model", "gpt-4o-mini")
        prompt_template = self.config.get("prompt", "")
        system_prompt = self.config.get("system_prompt")
        temperature = self.config.get("temperature", 0.7)
        max_tokens = self.config.get("max_tokens", 2048)

        # Resolve template variables
        prompt = context.resolve_template(prompt_template)

        provider = provider_registry.get(provider_name)
        if provider is None:
            return NodeResult(output=None, success=False, error=f"Provider '{provider_name}' not found")

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": context.resolve_template(system_prompt)})
        messages.append({"role": "user", "content": prompt})

        try:
            response = await provider.chat(
                messages=messages,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return NodeResult(output=response, metadata={"provider": provider_name, "model": model})
        except Exception as e:
            return NodeResult(output=None, success=False, error=str(e))

    def validate_config(self) -> list[str]:
        errors = []
        if not self.config.get("prompt"):
            errors.append(f"Node {self.node_id}: 'prompt' is required for LLM nodes")
        return errors
