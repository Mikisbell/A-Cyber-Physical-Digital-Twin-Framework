# Skill: Paper Production Pipeline

## Trigger
Load when: generating a draft, compiling PDF, running validate_submission, or managing paper status flow.

## SDD Flow for Papers

Every paper follows this DAG (not waterfall — if verify fails, loop back):

```
EXPLORE → SPEC → DESIGN → TASKS → IMPLEMENT → VERIFY
  ↑                                              |
  └──────────── FAIL → diagnose → fix ───────────┘
```

### 1. EXPLORE
- Read `config/params.yaml` to confirm active domain
- Check `data/processed/` for available datasets
- Search Engram for prior decisions on this topic
- Read `.agent/specs/journal_specs.yaml` for target quartile gates

### 2. SPEC
- Define: title, domain, quartile, target journal
- Set word count target from journal_specs.yaml
- List required figures (numbered: fig_01, fig_02...)
- List required data sources from data/processed/
- Write spec to Engram: `mem_save("paper_spec: {title} targeting {journal}")`

### 3. DESIGN
- Outline IMRaD sections with estimated word counts per section
- Map figures to sections
- Map references to sections (use bibliography_engine categories)
- Identify which sub-agents needed (Verifier, Figure Agent, etc.)

### 4. TASKS
- Break into atomic tasks: one section = one task
- Each task has: input data, output section, validation criteria
- Tasks are independent where possible (Results needs Methodology done first)

### 5. IMPLEMENT
- Generate each section via scientific_narrator.py or manual writing
- Generate figures via plot_figures.py
- Generate BibTeX via generate_bibtex.py
- Each section gets `<!-- AI_Assist -->` markers

### 6. VERIFY
- Run `validate_submission.py` — must pass all checks
- Run Verifier sub-agent if paper includes numerical results
- Check against journal_specs.yaml quality gates
- If FAIL: identify which gate failed, loop back to relevant step

## Status Flow
```
draft → review → submitted → accepted
```
- `draft`: actively being written/generated
- `review`: all sections complete, pending HV markers from Mikisbell
- `submitted`: sent to journal, awaiting reviewer response
- `accepted`: published or accepted for publication

## Engram Protocol for Papers
After each paper event, log:
- `mem_save("paper_event: [draft|review|submitted|accepted] {title}")`
- `mem_save("paper_decision: chose {journal} because {reason}")`
- `mem_save("paper_error: {validation_check} failed — {fix_applied}")`

## Tools Reference
| Step | Tool | Command |
|------|------|---------|
| Generate draft | `articles/scientific_narrator.py` | `--domain X --quartile QN --topic "..."` |
| Generate figures | `tools/plot_figures.py` | `--domain X` |
| Generate BibTeX | `tools/generate_bibtex.py` | `--output articles/references.bib` |
| Validate | `tools/validate_submission.py` | `articles/drafts/paper_*.md` |
| Compile PDF | `tools/compile_paper.sh` | `draft.md --template ieee\|conference\|elsevier` |
| Cover letter | `tools/generate_cover_letter.py` | `cover --draft draft.md` |
