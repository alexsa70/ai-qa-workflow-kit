# Component Inventory

## Purpose

This document records existing QA agents, skills, workflows, artifacts, and
supporting tools that may contribute to `ai-qa-workflow-kit`.

It is an analysis backlog, not a migration manifest. Nothing listed here should
be copied into the kit until its reusable contract is separated from project
and AI-platform details.

## Decision Labels

| Label | Meaning |
|---|---|
| `adopt` | Reuse the component with small portability changes. |
| `extract` | Extract a reusable core from a project-specific implementation. |
| `adapter` | Keep outside the core and expose through project configuration or an integration adapter. |
| `reference` | Preserve as design evidence or an example, but do not make it an active component. |
| `exclude` | Do not migrate generated, duplicated, obsolete, or unsafe material. |
| `review` | Valuable candidate whose final role is not decided yet. |

## Source Registry

| Priority | Source | Contents | Authority | Initial decision |
|---:|---|---|---|---|
| 1 | `/Users/alex/MyRepos/qa` | 15 agents, 25 skills, contracts, templates, reviewers, gates, and automation workflows | Most complete and current QA workflow source found | Primary extraction source |
| 2 | `/Users/alex/.codex/skills` | Reusable Python, pytest, FastAPI, Playwright, and review-verification skills | Current Codex-oriented reusable skills | Adopt or reference through dependencies |
| 3 | `/Users/alex/Documents/qa-agents` | Provider-neutral role rules, launcher scripts, dashboard, shared engineering rules | Early portable QA-agent prototype | Extract principles and launcher lessons |
| 4 | `/Users/alex/MyRepos/work/api_new_fraimwork` | Simple QA Orchestrator and API-test role chain | Current first consumer project | Use as integration case and project adapter |
| 5 | `/Users/alex/MyRepos/qa/e2e-ui-tests` | Playwright planner, generator, healer, UI coordinator, author, and reviewer roles | Current UI-specific workflow source | Extract UI workflow contracts |
| 6 | `/Users/alex/MyRepos/work/qa` | Earlier subset of `/Users/alex/MyRepos/qa` | Older or reduced copy | Reference only; prefer newer source |
| 7 | `/Users/alex/MyRepos/node-merged-kal` | Small `gen-test` skill and test-reviewer role | Narrow project-specific prototype | Reference only |

## Core Architecture Candidates

| Component | Type | Best source | Reusable value | Project/platform coupling to remove | Decision | Priority |
|---|---|---|---|---|---|---:|
| QA Orchestrator | Agent | Current kit plus `/Users/alex/MyRepos/qa/.claude/skills/qa-auto` | Classification, routing, gates, completion control | Claude tool names, model tiers, project paths, nested-agent assumptions | `adopt` | P0 |
| Project context | Configuration artifact | Current kit `templates/project-context.md` | Separates reusable workflow from repository facts | Markdown-only format may be difficult to validate mechanically | `adopt` | P0 |
| Task contract | Artifact schema | Current kit `agents/qa-orchestrator.md` | Standard task intake and scope boundary | Needs stable status and version fields | `adopt` | P0 |
| Handoff contract | Artifact schema | Current kit and `qa-auto/CONTRACTS.md` | Safe context transfer between roles | Claude-specific dispatch payloads and tool names | `extract` | P0 |
| Worker return | Artifact template | `spec-first-test/templates/worker-return.md` and UI equivalent | Structured files, blockers, checks, and shared-file requests | API/UI field differences and Claude worker lifecycle | `extract` | P0 |
| Gate report | Artifact template | `qa-lead`, `ui-qa-lead`, and quality-gate files | Evidence-backed PASS, AMEND, or FAIL decision | Project-specific commands and checklist items | `extract` | P0 |
| Source-of-truth verdict | Artifact template | `source-of-truth` | Answer, authority, contradictions, confidence, and action | Kal Sense authority hierarchy and Outline/Keycloak paths | `extract` | P1 |
| Coverage matrix | Artifact schema | `coverage-plan` | Explicit applicable, covered, missing, and waived dimensions | Fixed project taxonomy and TestMO naming | `extract` | P1 |
| Approval record | Artifact schema | Existing confirmation gates | Durable evidence of approved scope and transition | Currently often exists only in conversation | `review` | P1 |
| Verification result | Artifact schema | Review skills and QA gate agents | Records command, scope, result, and limitations | Commands differ by project | `extract` | P1 |

## Agent Candidates

| Candidate | Best source | Distinct decision ownership | Reusable core | Keep in project adapter | Decision |
|---|---|---|---|---|---|
| QA Orchestrator | Current kit, `qa-auto`, `coordinator` | Own workflow state, routing, approvals, and completion | Task classification, executor selection, gate evaluation | Available tools, commands, project policies | `adopt` |
| QA Strategist | `Documents/qa-agents/rules/strategist.md` | Convert raw requirements into an ordered QA backlog | Scope decomposition, priority, dependencies, risks | Project priority conventions and target systems | `extract` |
| Test Case Designer / STD Drafter | `test-case-designer.md`, `std-drafter.md`, `manual-test-plan` | Turn confirmed behavior into reviewable test designs | Test structure, readiness, traceability, cleanup | Test management fields and project taxonomy | `extract` |
| API Test Author | `api-test-author.md`, `qa-engineer.md` | Implement approved API-test designs | Read neighboring code, reuse layers, report wiring needs | Client architecture, schemas, fixtures, markers | `extract` |
| UI Test Author | `ui-test-author.md` | Implement approved UI-test designs | Page/fixture/spec separation and structured return | Playwright conventions, paths, selectors, fixtures | `extract` |
| Coverage Strategist | `coverage-strategist.md` | Determine applicable coverage dimensions and gaps | Applicability, evidence, coverage matrix | Dimension taxonomy and source locations | `extract` |
| QA Lead | `qa-lead.md`, `ui-qa-lead.md` | Independent completion gate and escalation | Evidence-based gate, bounded revision rounds | Concrete commands and project rules | `extract` |
| Design Reviewer | `qa-design-reviewer.md` | Validate spec fidelity and authority chain | Independent design review | Product-specific source hierarchy | `extract` |
| Functional Reviewer | `qa-functional-reviewer.md` | Validate expected behavior and executable assertions | Scenario correctness and false-positive resistance | Framework conventions | `extract` |
| Coverage Reviewer | `qa-coverage-reviewer.md` | Audit claimed coverage and waivers | Gap, regression, redundancy, and evidence checks | Fixed 12-dimension taxonomy | `extract` |
| Write Reviewer | `qa-write-reviewer.md` | Validate external write payload and resulting artifact | Mechanical write verification and consistency | TestMO/Jira payload formats | `extract` |
| ISTQB Reviewer | `qa-istqb-reviewer.md` | Review test design quality independently | Test technique and traceability review | Organization-specific test templates | `extract` |
| Bug Investigator / Healer | `playwright-test-healer.md`, current bug-fixing role | Reproduce, classify, repair, and reverify failures | Root-cause workflow and assertion-preservation rule | Browser tools and framework commands | `extract` |
| PR Reviewer | `pr-reviewer.md` | Adversarial change review with empirical evidence | Evidence, severity, scenario, fix, verification | GitHub API, Jira, Outline, branch conventions | `extract` |
| Retrospective Author | `retrospective-author.md` | Summarize completed workflow evidence and lessons | Artifact-based retrospective | Project-specific output format | `reference` |
| Autonomous Decision Advisor | `qa-autonomous-engineer.md` | Resolve one ambiguous next-action decision independently | Focused evidence-in/verdict-out contract | Claude agent implementation | `reference` |
| Team Lead | `team-lead.md` | General engineering sprint coordination | File ownership and shared-file wiring | Broader than QA workflow kit scope | `reference` |

## Skill Candidates

| Candidate | Best source | Reusable procedure | Coupling to isolate | Decision | Priority |
|---|---|---|---|---|---:|
| `source-of-truth` | Current kit, extracted from `/Users/alex/MyRepos/qa/.claude/skills/source-of-truth` | Resolve conflicting sources using project-defined authority, freshness, evidence, and confidence | Project source policy and available integrations | `adopt` | P0 |
| `api-layered-architecture` | Current kit, extracted from the user's original API framework architecture and `qa/api-tests` four-layer pattern | Map and enforce transport, service-client, schema, factory, assertion, and test responsibilities for API automation | Project-specific path names and allowed exceptions | `adopt` | P0 |
| `code-review` | Current kit, extracted from review candidates and existing Codex review skills | Review QA automation changes against approved contracts, source evidence, cleanup, traceability, and verification | Stack-specific review commands and adapters | `adopt` | P0 |
| `bug-fixing` | Current kit, extracted from bug-fixing and healer candidates | Reproduce, classify, and repair QA automation failures while preserving approved expectations and cleanup safety | Project commands, runtime access, and product bug tracker adapters | `adopt` | P0 |
| `review-verification-protocol` | `/Users/alex/.codex/skills/review-verification-protocol` | Verify findings before reporting them | Codex skill references only | `adopt` | P0 |
| `consistency-sweep` | `/Users/alex/MyRepos/qa/.claude/skills/consistency-sweep` | Detect unresolved placeholders after external writes | Current integration names and default patterns | `adopt` | P0 |
| `spec-first-test` | `/Users/alex/MyRepos/qa/.claude/skills/spec-first-test` | Move from confirmed spec and test design to API automation | Kal Sense sources, Claude gates, pytest architecture | `extract` | P1 |
| `spec-first-ui-test` | `/Users/alex/MyRepos/qa/.claude/skills/spec-first-ui-test` | Move from UI spec and test design to Playwright automation | Kal Sense UI structure and Claude teams | `extract` | P1 |
| `coverage-plan` | `/Users/alex/MyRepos/qa/.claude/skills/coverage-plan` | Create or audit explicit coverage matrices | Fixed 12 dimensions, Keycloak and TestMO | `extract` | P1 |
| `manual-test-plan` | `/Users/alex/MyRepos/qa/.claude/skills/manual-test-plan` | Requirements-to-test-design pipeline with quality review | Jira, TestMO, Kal Sense authority chain | `extract` | P1 |
| `testmo` family | `/Users/alex/MyRepos/qa/.claude/skills/testmo` | Search, draft, amend, mark, and reconcile test cases | TestMO API and project field mappings | `adapter` | P1 |
| `qa-auto` | `/Users/alex/MyRepos/qa/.claude/skills/qa-auto` | Autonomous orchestration pattern and reviewer fanout | Claude main-turn limitations, GitHub, Jira, TestMO, product rules | `reference` | P1 |
| `file-bug` | `/Users/alex/MyRepos/qa/.claude/skills/file-bug` | Convert confirmed runtime deviation into a bug artifact | Jira project and issue fields | `extract` | P2 |
| `sync-docs` | `/Users/alex/MyRepos/qa/.claude/skills/sync-docs` | Synchronize external requirements into a local evidence store | Outline API and local manifest format | `adapter` | P2 |
| `probe-runtime` | `/Users/alex/MyRepos/qa/aiq-toolbelt` | Collect runtime evidence for thresholds and environment behavior | Kubernetes topology and service configuration | `adapter` | P2 |
| `pr-review` | `/Users/alex/MyRepos/qa/.claude/skills/pr-review` | Evidence-backed PR review workflow with publish gate | GitHub CLI/API, Jira, Outline, project recipes | `extract` | P2 |
| `systematic-debugging` | `/Users/alex/MyRepos/qa/.claude/skills/superpowers/systematic-debugging` | Reproduce, isolate, hypothesize, test, and verify | Generic; licensing and provenance must be checked | `review` | P2 |
| `pytest-api-code-review` | `/Users/alex/.codex/skills/pytest-api-code-review` | Review or create pytest API tests using local patterns | Python/pytest stack | `adapter` | P2 |
| `playwright-e2e-code-review` | `/Users/alex/.codex/skills/playwright-e2e-code-review` | Review UI fixtures, pages, specs, and visual tests | Playwright stack | `adapter` | P2 |
| `python-code-review` | `/Users/alex/.codex/skills/python-code-review` | Baseline Python review | Python stack | `adapter` | P3 |
| `pytest-code-review` | `/Users/alex/.codex/skills/pytest-code-review` | Baseline pytest review | pytest stack | `adapter` | P3 |
| `fastapi-code-review` | `/Users/alex/.codex/skills/fastapi-code-review` | Review API implementation contracts | FastAPI stack | `adapter` | P3 |
| `playwright-skill` | `/Users/alex/MyRepos/qa/.claude/skills/playwright-skill` | Browser automation procedure and helper runtime | Node package, browser installation, Claude invocation | `review` | P3 |
| `graphify` | `/Users/alex/MyRepos/qa/.claude/skills/graphify` | Query and refresh repository knowledge graph | External tool availability | `adapter` | P3 |
| `outline-mcp` | `/Users/alex/MyRepos/qa/.claude/skills/outline-mcp` | Tool-selection guidance for Outline | Outline connector | `adapter` | P3 |
| `resolveconflicts` | `/Users/alex/MyRepos/qa/.claude/skills/resolveconflicts` | Resolve merge conflicts systematically | Git workflow policy | `review` | P3 |
| `autoresearch` | `/Users/alex/MyRepos/qa/.claude/skills/autoresearch` | Evidence-driven technical investigation | Claude tools and unusually exhaustive default | `reference` | P3 |

## Artifact And Template Candidates

| Artifact | Source | Consumer | Reusable fields | Decision |
|---|---|---|---|---|
| Project context | Current kit | Orchestrator and all procedures | Identity, technology, paths, commands, policies, capabilities | `adopt` |
| Task contract | Current kit | Orchestrator | Objective, scope, facts, unknowns, executor, gates, verification | `adopt` |
| Handoff payload | Current kit and `qa-auto/CONTRACTS.md` | Specialist agent or skill | Objective, evidence, constraints, output, completion gate | `extract` |
| Worker return | API/UI `worker-return.md` | Coordinator | Status, files, shared-file requests, checks, blockers | `extract` |
| API contract report | API discovery role and `source-of-truth` | Test designer and implementer | Method, path, auth, schemas, statuses, confidence, evidence | `extract` |
| Test design | `test-design/`, manual-test-plan, TestMO templates | Implementation agent | Status, source, actors, steps, assertions, cleanup, readiness | `extract` |
| Coverage matrix | `coverage-plan` | Strategist and coverage reviewer | Target, dimension, applicability, evidence, coverage, waiver | `extract` |
| Gate report | QA lead agents | Orchestrator and user | Check, result, evidence, verdict, amendment request | `extract` |
| Reviewer verdict | QA reviewer agents | Orchestrator | Rule, severity, evidence, suggested edit, next action | `extract` |
| Source verdict | `source-of-truth` | Any workflow | Answer, authority, citation, contradictions, confidence, action | `extract` |
| TestMO update note | `spec-first-*` templates | Test management adapter | Mismatch, authority, proposed update, approval status | `adapter` |
| Bug ticket | `file-bug/templates/bug-ticket.md` | Issue tracker adapter | Observed, expected, evidence, impact, reproduction | `extract` |
| Verification result | QA lead and review skills | Completion gate | Command, scope, exit/result, timestamp, limitations | `extract` |
| Retrospective | Retrospective author | Humans and future workflows | Planned, completed, blocked, learned, action items | `reference` |

## Shared Rules Worth Extracting

| Rule | Source | Target location |
|---|---|---|
| Never invent endpoints, fields, selectors, credentials, or paths | `shared-engineering-rules.md` and current roles | Core guardrails |
| Separate planning, documentation, implementation, and review | `shared-engineering-rules.md` | Core workflow policy |
| Preserve approved test intent while fixing failures | Bug-fixing roles | Core repair policy |
| Use executable evidence before declaring completion | QA leads and review protocol | Core verification policy |
| Require cleanup for persistent test data | API and UI roles | QA domain policy |
| Keep workers away from shared files; coordinator performs wiring | Coordinator workflows | Optional parallel-execution policy |
| A reviewer must not self-certify without evidence | QA lead and reviewer roles | Core gate policy |
| Limit revision loops and escalate instead of looping forever | QA lead and autonomous workflows | Core failure policy |
| Keep user interaction with the main orchestrator | Coordinator and `qa-auto` | Platform capability policy |
| Treat runtime agents and Markdown role files as different things | Current kit and current project | Core terminology |

## Platform Adapters

| Platform | Existing evidence | Adapter responsibility | Core must not assume |
|---|---|---|---|
| Codex | `AGENTS.md`, `.codex/agents/*.toml`, `~/.codex/skills` | Instruction discovery, skill installation, tool mapping, local file links | Codex tools are always present |
| Claude Code | `.claude/agents`, `.claude/skills`, Agent/TeamCreate/AskUserQuestion workflows | Frontmatter, subagent dispatch, model selection, user gates | Claude agent teams or nested dispatch are available |
| Generic CLI | `Documents/qa-agents/bin/qa-agent` | Assemble role plus shared rules and start provider | Provider accepts the same flags or prompt format |
| GitHub | `pr-review` | Fetch PR evidence, publish comments, preserve review state | Network access and `gh` authentication |
| TestMO | `testmo` family | Search, draft, amend, mark, map project fields | TestMO is the authority for expected behavior |
| Outline | `outline-mcp`, `sync-docs` | Fetch current documents and maintain local freshness | Outline is configured in every project |
| Jira | `manual-test-plan`, `file-bug`, `qa-auto` | Fetch requirements and create approved tickets | Jira issue types and fields are universal |
| Kubernetes runtime | `probe-runtime` | Gather runtime configuration evidence | Cluster access is available |

## Exclusions And Duplicate Rules

| Material | Decision | Reason |
|---|---|---|
| `node_modules/**/agents/*` | `exclude` | Third-party generated/package material, not the user's reusable source |
| `.claude/worktrees/**` | `exclude` | Temporary duplicate worktree content |
| `/Users/alex/MyRepos/work/qa` duplicates | `exclude` when identical | Prefer the newer `/Users/alex/MyRepos/qa` source |
| Hardcoded `/Users/liorco/...` paths | `adapter` | Replace with project context variables |
| Kal Sense, Everest, Keycloak service maps, role names, marker lists | `adapter` | Product-specific policy and source mapping |
| Claude model names and model-tier rules | `adapter` | Platform and account dependent |
| Actual credentials, tokens, `.env` values | `exclude` | Secrets must never enter the kit |
| Generated outputs and logs | `exclude` | Runtime evidence, not reusable component definitions |
| Old launcher dashboard UI | `reference` | Useful product idea, but not required for core architecture |

## Proposed Extraction Order

1. Keep the QA Orchestrator as the single entry agent; place repeatable
   procedures in skills.
2. Define versioned schemas for project context, task contract, handoff, worker
   return, gate report, and verification result.
3. Adopt `review-verification-protocol` as the first external reusable skill.
4. Validate the generic `source-of-truth` skill against two project contexts.
5. Adopt `consistency-sweep` with generic defaults and integration hooks.
6. Build the first end-to-end workflow:
   `orchestrator -> source-of-truth -> artifact -> gate`.
7. Connect `api_new_fraimwork` as the first project adapter.
8. Extract API test design and implementation roles only after the first chain
   is verified.
9. Add UI and TestMO adapters after the core contracts are stable.

## Open Decisions

- Should project context remain Markdown or gain a machine-readable YAML file?
- Which artifact schemas require JSON/YAML validation in the first release?
- Should stack review skills be bundled, installed as optional dependencies, or
  referenced by capability name?
- How should one workflow declare required capabilities without naming a
  specific AI provider's tools?
- Which source repository and license metadata must be preserved when extracting
  existing components?
