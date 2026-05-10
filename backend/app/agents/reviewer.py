"""Reviewer Agent — quality review with 5-dimension scoring via LLM."""

from app.llm.client import LLMClient


REVIEWER_SYSTEM_PROMPT = """你是一名内容质量审核专家。对给定的文章进行5维度评分，
并列出需要改进的问题。

5个评分维度：
1. 合规性（是否违规、敏感词、政治不正确）
2. 原创度（内容是否有独到见解，避免套话）
3. 可读性（行文流畅度、逻辑清晰度）
4. 风格一致性（是否符合作者/平台的一贯风格）
5. 平台适配性（是否符合目标平台的调性和规范）

每个维度0-100分。问题列表按严重程度排序：
- error: 严重问题（必须修改）
- warning: 建议修改
- info: 可优化项

请以 JSON 格式返回，严格按照以下结构：
{
  "overall_score": 85,
  "dimensions": {"合规性": 95, "原创度": 78, "可读性": 85, "风格一致性": 80, "平台适配性": 82},
  "issues": [
    {"section_index": 0, "text": "问题简述", "severity": "warning", "dimension": "可读性", "suggestion": "改进建议"}
  ],
  "summary": "整体评价（30字以内）"
}
"""

FORBIDDEN_WORDS_CHECK = """额外要求：如果文章包含以下禁用词，请在高违规的issues中标记：
{forbidden_words}
"""


class ReviewerAgent:
    """Quality review with 5-dimension scoring via LLM."""

    def __init__(self, llm_client: LLMClient | None = None):
        self.name = "reviewer"
        self._llm = llm_client or LLMClient()

    async def run(self, project_context: dict, article: dict,
                  platform: str) -> dict:
        """Review article content and return scores + issues."""
        forbidden = project_context.get("forbidden_words", [])

        # Build article text for review
        sections_text = ""
        for i, sec in enumerate(article.get("sections", [])):
            sections_text += f"\n[Section {i}] {sec.get('heading', '')}\n{sec.get('content', '')}\n"

        user_prompt = f"""目标平台：{platform}
项目风格：{project_context.get('writing_style', '未指定')}

文章内容：
{sections_text}
"""
        if forbidden:
            user_prompt += FORBIDDEN_WORDS_CHECK.format(forbidden_words=", ".join(forbidden))

        messages = [
            {"role": "system", "content": REVIEWER_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ]

        result = await self._llm.chat_json(messages=messages, temperature=0.3)
        data = result["content"]

        return {
            "overall_score": data.get("overall_score", 60),
            "dimensions": data.get("dimensions", {}),
            "issues": data.get("issues", []),
            "summary": data.get("summary", ""),
        }
