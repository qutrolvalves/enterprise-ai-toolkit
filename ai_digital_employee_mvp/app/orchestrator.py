"""
Agent 编排器。

并行调用所有 Agent，聚合结果。
支持部分失败：单个 Agent 出错不影响其他 Agent。
"""

import asyncio
import logging
from .agents.agent import call_agent, AGENT_TYPES

logger = logging.getLogger(__name__)


async def orchestrate_request(message: str) -> dict:
    """
    并行调用所有 Agent 处理客户消息。

    Args:
        message: 客户消息。

    Returns:
        dict: Agent 类型 -> Agent 响应结果
              每个结果包含 status / agent / content 字段。
    """
    logger.info("开始编排请求: message=%s...", message[:50])

    # 并行调用所有 Agent
    results = await asyncio.gather(
        *(call_agent(agent_type, message) for agent_type in AGENT_TYPES),
        return_exceptions=True,
    )

    # 整理结果
    output = {}
    for agent_type, result in zip(AGENT_TYPES, results):
        if isinstance(result, Exception):
            logger.error("Agent %s 抛出未处理异常: %s", agent_type, result)
            output[agent_type] = {
                "status": "error",
                "agent": agent_type,
                "content": f"未知错误: {str(result)}",
            }
        else:
            output[agent_type] = result

    # 统计
    ok_count = sum(
        1 for r in output.values() if r.get("status") == "ok"
    )
    logger.info("编排完成: %d/%d Agent 成功", ok_count, len(AGENT_TYPES))

    return output
