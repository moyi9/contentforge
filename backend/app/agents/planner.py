"""Planner Agent — generates and ranks content topic candidates via LLM."""

from app.llm.client import LLMClient


PLANNER_SYSTEM_PROMPT = """你是一名专业的内容策划编辑。你的任务是针对给定的主题和目标平台，
生成3个高质量选题候选，并为每个候选撰写大纲和评分。

评分标准（1-10）：
- 话题热度（是否当前受众关注）
- 差异化（与竞品内容的区别度）
- 可行性（选题的写作难度和资料可得性）
- 平台适配性（是否适合目标平台的调性）

请以 JSON 格式返回结果，严格按照以下结构：
{
  "candidates": [
    {
      "title": "选题标题",
      "outline": ["大纲点1", "大纲点2", ...],
      "score": 8.5
    }
  ],
  "analysis": "整体分析说明（30字以内）"
}
"""


class PlannerAgent:
    """Generates content topic candidates with outlines and scores via LLM."""

    def __init__(self, llm_client: LLMClient | None = None):
        self.name = "planner"
        self._llm = llm_client or LLMClient()

    async def run(self, project_context: dict, topic: str,
                  platform: str, target_audience: str) -> dict:
        """Generate and rank topic candidates using LLM."""
        project_name = project_context.get("name", "")
        writing_style = project_context.get("writing_style", "")

        user_prompt = f"""主题：{topic}
目标平台：{platform}
目标受众：{target_audience}
项目风格：{writing_style or '未指定'}
项目名称：{project_name or '未指定'}"""

        messages = [
            {"role": "system", "content": PLANNER_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ]

        result = await self._llm.chat_json(messages=messages, temperature=0.7)
        data = result["content"]

        # Ensure candidates are sorted by score descending
        data["candidates"].sort(key=lambda c: c.get("score", 0), reverse=True)

        return {
            "candidates": data.get("candidates", []),
            "topic": topic,
            "platform": platform,
            "analysis": data.get("analysis", ""),
        }
