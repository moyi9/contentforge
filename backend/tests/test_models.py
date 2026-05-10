import pytest
from pydantic import ValidationError
from app.models.project import Project
from app.models.knowledge import KnowledgeDoc
from app.models.task import TaskRequest, TaskStatus
from app.models.article import Article, Section, ImageSuggestion
from app.models.review import ReviewResult, ReviewIssue
from app.models.export import ExportRequest


def test_project_required_fields():
    with pytest.raises(ValidationError):
        Project()
    p = Project(
        id="proj-1",
        name="My Tech Blog",
        description="Personal tech writing",
        writing_style="technical, concise",
        forbidden_words=[],
        template_config={},
        knowledge_base_path="./vault/tech-blog",
    )
    assert p.name == "My Tech Blog"


def test_task_request_multiple_platforms():
    tr = TaskRequest(
        project_id="proj-1",
        topic="AI Agents in 2026",
        platforms=["公众号", "小红书"],
        content_type="technical",
        target_audience="developers",
        word_count=1500,
    )
    assert len(tr.platforms) == 2
    assert tr.word_count == 1500


def test_article_has_sections():
    article = Article(
        id="art-1",
        task_id="task-1",
        platform="公众号",
        title="AI Agents Guide",
        sections=[Section(heading="Intro", content="Hello")],
        image_suggestions=[],
        rag_sources=[],
        metadata={},
    )
    assert len(article.sections) == 1


def test_review_result():
    issue = ReviewIssue(
        section_index=0,
        text="use simpler words",
        severity="warning",
        dimension="可读性",
        rule_ref="style-1",
        suggestion="Use 'use' not 'utilize'",
        auto_fixed=False,
    )
    review = ReviewResult(
        article_id="art-1",
        overall_score=85.5,
        dimensions={"合规性": 95, "原创度": 82, "可读性": 88},
        baseline_comparison={"原创度": {"you": 82, "avg": 91}},
        issues=[issue],
        suggestions=["fix section 0"],
        passed=True,
    )
    assert review.passed


def test_export_request():
    req = ExportRequest(
        article_id="art-1",
        format="pdf",
        include_review_notes=False,
        include_image_suggestions=True,
    )
    assert req.format == "pdf"


def test_knowledge_doc():
    doc = KnowledgeDoc(
        id="doc-1",
        project_id="proj-1",
        title="Style Guide",
        content="# Style\nBe concise.",
        doc_type="style_guide",
        source_path="./vault/style.md",
        chunk_ids=[],
    )
    assert doc.doc_type == "style_guide"


def test_task_status_states():
    for state in ["pending", "planning", "awaiting_plan", "writing",
                   "awaiting_draft", "reviewing", "awaiting_review",
                   "exporting", "done", "failed"]:
        ts = TaskStatus(task_id="t1", state=state, current_agent="test")
        assert ts.state == state
    # Test defaults
    ts = TaskStatus(task_id="t1", state="pending", current_agent="test")
    assert ts.progress == 0.0
    assert ts.result is None
    assert ts.error is None


def test_word_count_rejects_negative():
    with pytest.raises(ValidationError):
        TaskRequest(project_id="p1", topic="x", platforms=["a"],
                    content_type="x", target_audience="x", word_count=-1)


def test_progress_out_of_range():
    with pytest.raises(ValidationError):
        TaskStatus(task_id="t1", state="pending", current_agent="x", progress=-1)
    with pytest.raises(ValidationError):
        TaskStatus(task_id="t1", state="pending", current_agent="x", progress=101)


def test_invalid_doc_type():
    with pytest.raises(ValidationError):
        KnowledgeDoc(id="d1", project_id="p1", title="x", content="x",
                     doc_type="bogus", source_path="x", chunk_ids=[])
