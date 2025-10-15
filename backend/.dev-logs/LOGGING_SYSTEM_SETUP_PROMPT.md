# Universal Development Logging System Setup Prompt

**Purpose:** Use this prompt in a separate Augment workspace to create a comprehensive development logging and task tracking system for any software project.

**Created:** 2025-10-09  
**Version:** 1.0

---

## 📋 Copy-Paste Prompt Below

```
Create a comprehensive development logging and task tracking system for my software project.

## Quick Project Context
Before starting, ask me these 3 questions:
1. What is your project name and primary programming language(s)?
2. What is your main project folder structure? (e.g., backend/, frontend/, src/, etc.)
3. Where should logs be stored? (default: .dev-logs/ in project root)

## Core Requirements

### 1. Folder Structure
Create a `.dev-logs/` directory with:
```
.dev-logs/
├── README.md                          # System documentation
├── TASKLIST.md                        # Master task tracker
├── logs/                              # Daily development logs
│   └── {ID}_{YYYY-MM-DD}_{description}.md
├── phase-summaries/                   # Milestone/phase summaries
│   └── phase-{N}_{name}.md
├── test-results/                      # Test execution results
│   └── {YYYY-MM-DD}_{suite}.json
├── decisions/                         # Technical decisions (ADRs)
│   └── {ID}_{topic}.md
└── issues/                            # Bug tracking
    └── {ID}_{description}.md
```

### 2. TASKLIST.md Structure
```markdown
# {Project Name} Task List

**Tech Stack:** {Languages/Frameworks}
**Current Phase:** {Phase Number/Name}
**Status:** {Overall Status}
**Last Updated:** {Date}

---

## Progress Summary
- [x] Phase 1: {Name} - COMPLETE
- [/] Phase 2: {Name} - IN PROGRESS
- [ ] Phase 3: {Name} - NOT STARTED

## Current Tasks
### Phase {N}: {Name}
- [ ] Task 1: Description
  - [ ] Subtask 1.1
  - [ ] Subtask 1.2
- [/] Task 2: Description (IN PROGRESS)
- [x] Task 3: Description (COMPLETE)

## Metrics
| Metric | Count |
|--------|-------|
| Files | X |
| Tests | Y |
| Coverage | Z% |

## Next Steps
1. {Next action}
2. {Next action}
```

### 3. Log Entry Template
```markdown
# {Title}

**Date:** {YYYY-MM-DD}
**Phase:** {Phase}
**Status:** ✅ COMPLETE / 🔄 IN PROGRESS / ❌ FAILED / ⚠️ BLOCKED

---

## Summary
{Brief overview}

## What Was Done
- {Accomplishment 1}
- {Accomplishment 2}

## Technical Details
### {Section}
- Implementation notes
- Code changes
- File paths

## Testing
- Test results
- Issues found
- Coverage changes

## Commits
- {commit hash}: {message}

## Time Spent
{X hours/days}

## Next Steps
- [ ] {Action 1}
- [ ] {Action 2}

## Blockers/Issues
- {Issue if any}
```

### 4. Automation Scripts
Create utility scripts in the language of my project (Python/Node.js/Shell) for:

**Core Operations:**
- `create_log.{ext}` - Generate new log entry with template
- `update_tasks.{ext}` - Update task status in TASKLIST.md
- `generate_summary.{ext}` - Create phase/milestone summary
- `search_logs.{ext}` - Search logs by keyword/date/phase
- `export_report.{ext}` - Generate progress report

**Script Features:**
- Auto-detect git branch, commits, and changes
- Extract test results from test runners
- Parse file changes and statistics
- Update TASKLIST.md automatically
- Generate timestamps and metadata

**Example Usage:**
```bash
# Create new log
./scripts/create_log --title "Feature Implementation" --phase 2

# Update task
./scripts/update_tasks --task "2.1" --status complete

# Search logs
./scripts/search_logs --keyword "database" --from "2025-01-01"

# Generate report
./scripts/export_report --phase 2 --format markdown
```

### 5. Git Integration
- Add `.dev-logs/` to `.gitignore` (logs stay local)
- Optional: Git hooks to auto-log commits
- Extract commit messages for log entries
- Track branch and merge information

### 6. Task States
Use these standard states:
- `[ ]` - Not Started
- `[/]` - In Progress
- `[x]` - Complete
- `[-]` - Cancelled
- `[!]` - Blocked

### 7. Naming Conventions
**Log Files:** `{ID}_{YYYY-MM-DD}_{kebab-case-description}.md`
- ID: 3-digit sequential (001, 002, 003...)
- Date: ISO format
- Description: Short, descriptive

**Examples:**
- `001_2025-10-09_initial-setup.md`
- `002_2025-10-09_database-migration.md`
- `003_2025-10-10_api-implementation.md`

### 8. Metadata Tracking
Auto-capture in each log:
- Timestamp
- Git branch & commit hash
- Files modified (count & paths)
- Lines added/removed
- Test pass/fail status
- Time spent (if tracked)
- Author/developer

### 9. Search & Query Features
Provide ability to:
- Filter by date range
- Search by keyword
- Filter by phase/milestone
- Filter by status
- Export filtered results
- Generate statistics

### 10. Best Practices
- Use markdown for all documentation
- Include code snippets with syntax highlighting
- Use emojis for visual clarity (✅ ❌ 🔄 ⚠️ 📊 🐛 🚀)
- Keep logs concise but informative
- Update TASKLIST.md regularly
- Archive old logs periodically
- Never commit logs to version control

## Deliverables
1. Complete `.dev-logs/` folder structure
2. README.md with usage instructions
3. TASKLIST.md initialized with current project state
4. Automation scripts in appropriate language
5. Log templates (markdown files)
6. Search/query utilities
7. Git integration (optional)
8. Quick start guide

## Technical Implementation
- Use native file I/O for the project's language
- JSON for structured data storage
- Markdown for human-readable logs
- Git integration via CLI or libraries
- Cross-platform compatibility (Windows/Mac/Linux)
- Error handling and validation
- Colorized terminal output (optional)

## Output Format
After implementation, provide:
1. Summary of what was created
2. Quick start commands
3. Example workflow
4. Customization options
5. Troubleshooting guide

Please implement this system with production-grade code quality, comprehensive error handling, and clear documentation. Adapt the implementation to match my project's tech stack and conventions.
```

---

## Usage Instructions

1. **Copy the entire prompt** from the code block above
2. **Open a new Augment workspace** (or any AI coding assistant)
3. **Paste the prompt** and answer the 3 context questions
4. **Review the generated system** and customize as needed
5. **Integrate with your workflow** using the provided scripts

## Notes

- This prompt is technology-agnostic and works for any programming language
- The generated system will adapt to your project's structure
- All logs remain local and are not committed to version control
- Scripts will be generated in your project's primary language

---

**Maintained by:** ConvergeAI Development Team  
**Last Updated:** 2025-10-09

