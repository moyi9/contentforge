"""Reviewer Agent — evaluates content quality across 5 dimensions"""

import re


class ReviewerAgent:
    """Reviews generated articles across 5 quality dimensions.
    Detects forbidden words, scores quality, and provides fix suggestions.
    In production this would use an LLM for deeper analysis."""

    DIMENSIONS = ["合规性", "原创度", "可读性", "风格一致性", "平台适配性"]

    def __init__(self):
        self.name = "reviewer"

    async def run(self, article: dict, project_context: dict) -> dict:
        """Review an article and return quality report."""
        forbidden_words = [w.lower() for w in project_context.get("forbidden_words", [])]
        all_text = self._extract_text(article)

        issues = []

        # Check forbidden words
        for word in forbidden_words:
            pattern = re.compile(re.escape(word), re.IGNORECASE)
            for i, section in enumerate(article.get("sections", [])):
                content = section.get("content", "")
                for match in pattern.finditer(content):
                    issues.append({
                        "section_index": i,
                        "text": match.group(),
                        "severity": "error" if len(word.split()) > 2 else "warning",
                        "dimension": "合规性",
                        "rule_ref": f"forbidden_word:{word}",
                        "suggestion": f"Remove forbidden word '{match.group()}'",
                        "auto_fixed": False
                    })

        # Score dimensions
        forbidden_count = len([i for i in issues if i["dimension"] == "合规性"])
        compliance_score = max(0, 100 - forbidden_count * 15)

        # Content length check
        total_chars = len(all_text)
        readability_score = min(100, max(20, total_chars // 2)) if total_chars > 0 else 50

        dimensions = {
            "合规性": compliance_score,
            "原创度": 80,  # Placeholder - real impl uses similarity check
            "可读性": readability_score,
            "风格一致性": 75,  # Placeholder
            "平台适配性": 85   # Placeholder
        }

        overall_score = sum(dimensions.values()) / len(dimensions)
        passed = compliance_score >= 80 and overall_score >= 70

        suggestions = [i["suggestion"] for i in issues]

        return {
            "article_id": article.get("title", "unknown"),
            "overall_score": round(overall_score, 1),
            "dimensions": dimensions,
            "baseline_comparison": {
                "原创度": {"you": 80, "avg": 85},
                "可读性": {"you": readability_score, "avg": 78}
            },
            "issues": issues,
            "suggestions": suggestions,
            "passed": passed
        }

    def _extract_text(self, article: dict) -> str:
        sections = article.get("sections", [])
        return " ".join(s.get("content", "") for s in sections)
