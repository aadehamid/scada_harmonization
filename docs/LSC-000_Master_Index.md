# LSC-000. Master index and architecture guide

Status: documentation organization for review. Existing project decisions retain
their recorded authority; numbering does not grant new approval.

Purpose: find the definition, contract, evidence, or learning guide for a task.
Dependencies: the project charter and the current handoff. This index owns
navigation and document identifiers, not scope or implementation status.

## Read in this order

1. [HANDOFF.md](../HANDOFF.md) sections 2 and 3 for current state and the next slice.
2. [LSC-001. Project charter](LSC-001_Problem_Statement_and_Project_Charter.md) for the problem, boundaries, architecture, and phase exits.
3. [Working conventions](WORKING_CONVENTIONS.md) and [development guide](DEVELOPMENT.md) before making changes.
4. Choose the subject below. Read [review standards](../REVIEW_STANDARDS.md) before reviewing a change.

## Document register

| ID | Document | Owns | Authority and review boundary |
| --- | --- | --- | --- |
| LSC-000 | This master index | Navigation and document IDs | Organization only; no design approval |
| LSC-001 | [Problem statement and project charter](LSC-001_Problem_Statement_and_Project_Charter.md) | Purpose, scope, planes, architecture, constraints, decisions, phase exits | Governing project definition; existing numbered sections remain intact |
| LSC-002 | [Domain model](LSC-002_Domain_Model.md) | Lagos Specialty Chemicals narrative | Domain explanation; charter wins on scope |
| LSC-003 | [Synthetic data strategy](LSC-003_Synthetic_Data_Generation_Strategy.md) | Layered generation approach | Strategy; contract and phase evidence govern implemented details |
| LSC-004 | [Level 0 contract](LSC-004_Level_0_Contract.md) | L0 records and replay identity | Component contract; not a PLC or Sparkplug contract |
| LSC-005 | [Phase 1 data record](LSC-005_Phase_1_Data_Record.md) | Landed Phase 1 implementation and persistence evidence | Dated record; [HTML reading copy](LSC-005_Phase_1_Data_Record.html) |
| LSC-006 | [Phase 1 datasheet](LSC-006_Phase_1_Datasheet.md) | Dataset roles and local versus R2 storage | Dated data record; [HTML reading copy](LSC-006_Phase_1_Datasheet.html) |
| LSC-007 | [Unit 100 engineering record](LSC-007_Unit_100_Engineering_Record.md) | Issued P&ID and tag schedule evidence | Engineering record; fixtures hold issued bytes |
| LSC-008 | [End-to-end walkthrough](LSC-008_End_to_End_Walkthrough.md) | Teaching sequence and diagram walkthrough method | Learning guide; charter defines architecture |
| LSC-009 | [Walkthrough progress](LSC-009_Walkthrough_Progress.md) | Walkthrough cursor and resume prompt | Learning continuity; handoff owns overall project status |
| LSC-010 | [Learning log](LSC-010_Learning_Log.md) | Durable concepts and shared glossary | Learning record; not a second design ledger |
| LSC-REG-001 | [Decision index](LSC-REG-001_Decision_Index.md) | Navigation to existing decision identifiers and evidence | Index only; preserve original qualifications |

Files keep their existing records and qualifications. Their document IDs come
from the filename and this register. Existing charter, phase, decision, and
walkthrough identifiers are unchanged.

## Find an architecture subject

All section numbers below refer to LSC-001. The charter remains one document so
existing section references and amendments keep their meaning.

| Question | Owning charter sections |
| --- | --- |
| What problem do we simulate, and for whom? | 1, 2, 6, 10 |
| What are the four planes? | 3 |
| Where do components and data live? | 4 and 4.1 |
| What differs among implementation variants? | 5 and 13.4 |
| How do the IT, OT, and ET sources relate? | 6 and 7 |
| What is the build order and acceptance evidence? | 8 and 8.1 |
| What constraints must implementation preserve? | 9 and 14 |
| What was decided, amended, or deferred? | 12, 13, and 14; LSC-REG-001 |
| Who governs metrics and identities? | 6, 9, 13.7, and 14.3 |
| How do reliability, commands, and zoning work? | 13.5, 13.8, 14.1, 14.2, and 14.4 |
| What feeds ML and graph reasoning? | 3, 13.5, and 14.6 |

## Repository responsibilities

| Location | Responsibility |
| --- | --- |
| `src/scada_harmonizer/datagen/` | Synthetic data and its layer boundaries |
| `src/scada_harmonizer/{harmonize,record,contextualize,apply}/` | The four planes; existence of a folder does not prove implementation |
| `config/` | Site and mapping configuration |
| `docker/` | Infrastructure configuration added by component |
| `notebooks/` | Marimo learning work; finalized code graduates to the package |
| `tests/fixtures/` | Small deterministic and issued engineering fixtures |
| `docs/assets/` | Reading-copy illustrations |
| `reference/` | Local-only reference evidence; see its [index](../reference/README.md) |

Current implementation state is recorded only in [HANDOFF.md section 2](../HANDOFF.md).

## Methods, history, and archives

- [Working conventions](WORKING_CONVENTIONS.md) own collaboration, diagrams, Git, and session discipline.
- [Development guide](DEVELOPMENT.md) owns commands and shared verification tools.
- [Review standards](../REVIEW_STANDARDS.md) own judgement rules learned from review incidents.
- [Session history](history/SESSION_LOG.md) preserves dated work and approval evidence.
- [Archive index](archive/README.md) separates superseded alternatives from the governing design.
- [Reorganization record](DOCUMENTATION_REORGANIZATION.md) records this batch's permission, source comparison, migration, and verification.

## What was combined

PPC's separate architecture, roadmap, governance, and technology documents are
combined here in the existing charter. Splitting approved sections would add
cross-reference work without resolving a missing definition. The source contract,
data records, engineering record, and learning guides remain separate because
they have different evidence and update cycles.

The reference does not add EPM dependencies, source systems, software choices,
or future component directories to this lab. Those require project decisions.
