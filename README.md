# AI 自动化测试用例生成项目

基于 CrewAI 的“场景驱动”测试生成项目。用户把业务场景描述放到指定文件后，
多个 Agent 会协作生成业务规则、业务场景、测试用例、测试数据、pytest 测试
代码和质量审查报告。

## 目录结构

```text
config/              环境配置
data/                本地数据库与数据生成脚本（gitignored）
input/               用户场景文件（gitignored，保留 .gitkeep）
scripts/             命令行工具
src/agents/          CrewAI Agent 定义
src/tasks/           CrewAI Task 定义
src/models/          Pydantic 输出模型
src/crew/            Crew 组合
src/database/        SQLite 访问
src/llm/             LLM 集成
skills/              Agent Skill
tool/                CrewAI 工具
business/            本地业务迁移（gitignored）
output/              生成产物（gitignored）
automated_tests/     生成的 pytest（gitignored）
samples/             可运行测试样本（提交）
```

## 环境准备

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

然后编辑 `.env`，填入你的模型接口配置。

## 快速开始

1. 把场景描述写到 `input/scenario.md`。
2. 运行完整流程：

```powershell
python scripts\run_pipeline.py
```

3. 运行本次生成的测试文件（以流水线输出为准）：

```powershell
python -m pytest automated_tests\test_orders.py -v
```

也可以指定其他场景文件，不需要覆盖默认输入：

```powershell
python scripts\run_pipeline.py --scenario-file input\scenario_orders.md
```

## 全流程

`run_pipeline.py` 按顺序执行 6 个 Agent：

```text
场景解析员    input/scenario.md → output/scenario_rules.json
数据库分析员  规则 + 数据库表结构 → output/business_scenarios.json
用例设计师    规则 + 场景 → output/test_cases.json
测试数据构造员 用例 + 规则 + 表结构 → output/test_data.json
自动化代码生成员 用例 + 数据 → automated_tests/*.py
质量审查员    全部产物 → output/coverage_report.json、output/review_report.md
```

## 单独运行

```powershell
python scripts\run_scenario_analyst.py
python scripts\run_database_analyst.py
python scripts\run_test_case_designer.py
python scripts\run_test_data_generator.py
python scripts\run_automation_code_generator.py
python scripts\run_qa_reviewer.py
```

代码生成员和审查员支持 `--reuse`，可以直接复用已有结果，不重新调用大模型。

## 测试样本

`samples/orders-rule-scenario/` 是一个可运行的完整样本，包含：

```text
sample.db                  带 orders 规则触发器的样本数据库
scenario.md                场景描述
scenario_rules.json        业务规则
business_scenarios.json    业务场景
test_cases.json            测试用例
test_data.json             测试数据
generated_test_suite.json  生成的测试套件
coverage_report.json       覆盖率报告
review_report.md           质量审查报告
automated_tests/           可执行 pytest
```

运行样本测试：

```powershell
python -m pytest samples\orders-rule-scenario\automated_tests -v
```

样本中的 `status` 枚举规则**故意没有在数据库实现**，所以运行样本测试会看到：

```text
24 passed
5 failed（全部为“规则未落地: status=...”）
```

这用来演示：当规则只存在于场景描述中、但数据库没有强制约束时，生成测试能
准确发现“规则未落地”。

## 注意事项

- `output/`、`automated_tests/` 都是生成产物，默认不提交。
- 数据库不提交；`samples/**/*.db` 作为测试样本数据库例外提交。
- `business/` 里的本地迁移脚本不提交，属于当前场景专属业务逻辑。
- 如果生成测试需要数据库里有对应字段和触发器，请先运行 `business/` 下的本地迁移脚本。
- 项目已通过 `.env` 关闭 CrewAI 遥测上传。
- 所有 Agent Task 都要求输出纯 JSON，避免模型不支持结构化输出时触发额外转换。
