"""Writer Agent — generates article content via LLM with RAG style constraints."""

from app.llm.client import LLMClient


WRITER_SYSTEM_PROMPT = """你是一名专业的内容写手。根据给定的大纲和写作风格，
生成完整的文章内容。

要求：
1. 内容需围绕大纲展开，每个章节500-800字
2. 使用目标平台的写作风格和语调
3. 如果有RAG参考上下文，将其风格融入内容
4. 内容要有信息量，避免空泛
5. 中文写作，专业但保持可读性

请以 JSON 格式返回，严格按照以下结构：
{
  "sections": [
    {"heading": "章节标题", "content": "章节内容（不少于200字）"}
  ]
}
"""


class WriterAgent:
    """Generates article content from an outline using LLM with RAG context."""

    def __init__(self, llm_client: LLMClient | None = None):
        self.name = "writer"
        self._llm = llm_client or LLMClient()

    async def run(self, project_context: dict, outline: dict,
                  platform: str, rag_context: list[str], word_count: int) -> dict:
        """Generate article sections from an outline using LLM."""
        title = outline.get("title", "Untitled")
        outline_items = outline.get("outline", [])
        writing_style = project_context.get("writing_style", "")

        rag_text = ""
        if rag_context:
            rag_text = "参考样式：\n" + "\n---\n".join(
                ctx[:500] for ctx in rag_context[:3]
            )

        user_prompt = f"""标题：{title}
大纲：{', '.join(outline_items)}
目标平台：{platform}
写作风格：{writing_style or '通用'}
目标字数：{word_count}
{rag_text}

请根据大纲为每个章节生成内容。"""

        messages = [
            {"role": "system", "content": WRITER_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ]

        result = await self._llm.chat_json(
            messages=messages,
            temperature=0.8,
            max_tokens=min(word_count * 2, 8192),
        )
        data = result["content"]
        sections = data.get("sections", [])

        # Attach RAG refs to sections that used them
        for section in sections:
            if rag_context:
                section["rag_ref"] = rag_context[0][:80]
            else:
                section["rag_ref"] = None

        return {
            "title": title,
            "sections": sections,
            "platform": platform,
            "metadata": {"word_count": word_count, "writing_style": writing_style},
        }
