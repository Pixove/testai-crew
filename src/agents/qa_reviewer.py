"""QA reviewer agent definition."""

from __future__ import annotations

from crewai import Agent, LLM
from crewai.skills import load_skill

from config.settings import PROJECT_ROOT, get_settings
from tool.inspect_database import InspectDatabaseTool
from tool.read_business_scenarios import ReadBusinessScenariosTool
from tool.read_scenario_rules import ReadScenarioRulesTool
from tool.read_test_cases import ReadTestCasesTool
from tool.read_test_data import ReadTestDataTool


def build_qa_reviewer() -> Agent:
    settings = get_settings()
    skill_path = PROJECT_ROOT / "skills" / "qa-review-checklist" / "SKILL.md"
    skills = load_skill(skill_path.read_text(encoding="utf-8"))
    return Agent(
        role="质量审查员",
        goal="审查测试覆盖情况，并评价最终测试效果",
        backstory=(
            "你是通用的测试质量评审专家，不依赖特定业务系统。你擅长检查规则是否"
            "被完整覆盖、组合是否遗漏，并给出可执行的改进建议和质量评分。"
        ),
        llm=LLM(
            model=settings.model_name,
            api_key=settings.api_key,
            base_url=settings.base_url,
        ),
        tools=[
            ReadScenarioRulesTool(),
            ReadBusinessScenariosTool(),
            ReadTestCasesTool(),
            ReadTestDataTool(),
            InspectDatabaseTool(),
        ],
        skills=skills,
        verbose=True,
    )
