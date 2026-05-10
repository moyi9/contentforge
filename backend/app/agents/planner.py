"""Planner Agent — generates and ranks content topic candidates"""


class PlannerAgent:
    """Generates content topic candidates with outlines and scores.

    In production this would call an LLM. For now it uses deterministic
    templates based on the project context and topic. This keeps tests
    fast and deterministic while the real LLM integration will be added
    via the MCP tool layer later.
    """

    def __init__(self):
        self.name = "planner"

    async def run(self, project_context: dict, topic: str,
                  platform: str, target_audience: str) -> dict:
        """Generate and rank topic candidates."""
        candidates = [
            {
                "title": f"{topic}: A Complete Guide for {target_audience}",
                "outline": [
                    "Introduction to " + topic,
                    "Key Concepts",
                    "Practical Applications",
                    "Best Practices",
                    "Conclusion",
                ],
                "score": 8.5,
            },
            {
                "title": f"How {topic} is Changing the Game in 2026",
                "outline": [
                    "The Old Way",
                    "The New Paradigm",
                    "Case Studies",
                    "What's Next",
                ],
                "score": 7.8,
            },
            {
                "title": f"Beginner's Roadmap to {topic}",
                "outline": [
                    "Why This Matters",
                    "Step-by-Step Guide",
                    "Common Mistakes",
                    "Resources",
                ],
                "score": 7.2,
            },
        ]

        # Sort by score descending
        candidates.sort(key=lambda c: c["score"], reverse=True)

        return {
            "candidates": candidates,
            "topic": topic,
            "platform": platform,
        }
