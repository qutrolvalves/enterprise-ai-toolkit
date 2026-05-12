"""
统一 AI Agent 模块。

将原来 4 个重复的 agent 文件合并为一个参数化模块，
使用 OpenAI SDK v1.0+ 异步客户端。
"""

import logging
from openai import AsyncOpenAI
from ..config import OPENAI_API_KEY

logger = logging.getLogger(__name__)

# 模型名称 — 使用 OpenAI 当前推荐的低成本模型
DEFAULT_MODEL = "gpt-4o-mini"

# 支持的所有 Agent 类型列表（与 AGENT_CONFIGS 的 key 保持一致）
AGENT_TYPES = ["sales", "tech", "quote", "followup"]

# Agent 配置：类型名 -> (显示名称, 提示词模板)
AGENT_CONFIGS = {
    "sales": {
        "name": "销售代理",
        "prompt_template": "你是一个专业的销售报价代理。请根据以下客户消息，生成详细的报价方案：\n\n{message}",
    },
    "tech": {
        "name": "技术代理",
        "prompt_template": "你是一个经验丰富的技术专家。请根据以下客户消息，分析客户的技术需求并提供技术建议：\n\n{message}",
    },
    "quote": {
        "name": "报价代理",
        "prompt_template": "你是一个资深的报价分析师。请根据以下客户消息，生成包含各项费用明细的详细报价单：\n\n{message}",
    },
    "followup": {
        "name": "跟进取暖",
        "prompt_template": "你是一个客户成功经理。请根据以下客户消息，制定后续跟进策略和沟通计划：\n\n{message}",
    },
}

# 全局异步客户端（惰性初始化）
_client: AsyncOpenAI | None = None


def _get_client() -> AsyncOpenAI | None:
    """获取或创建 OpenAI 异步客户端。"""
    global _client
    if _client is None and OPENAI_API_KEY:
        _client = AsyncOpenAI(api_key=OPENAI_API_KEY)
    return _client


async def call_agent(agent_type: str, message: str, model: str = DEFAULT_MODEL) -> dict:
    """
    调用指定类型的 AI Agent。

    Args:
        agent_type: Agent 类型，必须是 AGENT_CONFIGS 中的 key。
        message: 用户输入的消息。
        model: 使用的 OpenAI 模型名称。

    Returns:
        dict: {"status": "ok"|"error", "agent": str, "content": str}
    """
    config = AGENT_CONFIGS.get(agent_type)
    if not config:
        return {
            "status": "error",
            "agent": agent_type,
            "content": f"Unknown agent type: {agent_type}",
        }

    client = _get_client()
    if client is None:
        logger.error("OpenAI API key 未配置，无法调用 %s", config["name"])
        return {
            "status": "error",
            "agent": agent_type,
            "content": "OpenAI API key 未配置，请在 .env 中设置 OPENAI_API_KEY",
        }

    prompt = config["prompt_template"].format(message=message)

    try:
        logger.info("正在调用 %s (model=%s)...", config["name"], model)
        response = await client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            timeout=60,
        )
        content = response.choices[0].message.content or ""
        logger.info("%s 调用成功 (%d chars)", config["name"], len(content))
        return {
            "status": "ok",
            "agent": agent_type,
            "content": content,
        }
    except Exception as e:
        logger.error("%s 调用失败: %s", config["name"], str(e))
        return {
            "status": "error",
            "agent": agent_type,
            "content": f"调用 {config['name']} 失败: {str(e)}",
        }
