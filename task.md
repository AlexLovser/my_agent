# Hiring Task — AI Engineer Internship

**Description:** Design the tool contract that lets an LLM create and update levels and spaces in a housing inspection.

**Job posting:** https://app.notion.com/p/auditoo/Auditoo-recrute-29aa65fc8536803d8693d5aa86bae3ad?v=932cfc63a9114401ba584cf24989ff2d&source=copy_link

**Contact:** gauthier@auditoo.eco


## Context

Our AI agent never touches the database directly — every action goes through a **tool**: a typed function with a schema, called by an LLM. A badly designed tool makes the agent do the wrong thing silently: duplicate a space, clear a field nobody meant to clear, crash on a half-filled payload.

This task builds that tool layer for a small slice of our real domain: levels and spaces.

## Exercise

### Data model

- Two entity types: **level** and **space**
- A space belongs to exactly one level

### Tools

Implement tools to add and modify levels and spaces.

### Test payloads

Build a small runner that executes JSON tool-call payloads against an in-memory store. Handle at least:

```json
[
  {"tool": "insert_level", "args": {"name": "Rez-de-chaussée", "floor_number": 0}},
  {"tool": "insert_space", "args": {"name": "Cuisine", "level_id": "<id of level above>"}},
  {"tool": "update_space", "args": {"space_id": "<id above>", "non_visit_reason": "Pièce fermée à clé"}},
  {"tool": "update_space", "args": {"space_id": "<id above>", "name": "Cuisine ouverte"}},
  {"tool": "update_space", "args": {"space_id": "<id above>", "non_visit_reason": null}},
  {"tool": "insert_space", "args": {"name": "Chambre", "level_id": "lvl_does_not_exist"}},
  {"tool": "update_level", "args": {"level_id": "<id above>"}},
  {"tool": "insert_level", "args": {"floor_number": 1}}
]
```

### Stack

- Python
- [Pydantic](https://docs.pydantic.dev/latest/install/)

### Bonus — live tool-calling _(optional)_

Wire your tools into a real agent with a model (your own API key). Feed it 3-4 natural-language French instructions, e.g. *"Ajoute une chambre au premier étage"*.

## Deliverables

| Deliverable | Details |
| --- | --- |
| **GitHub repo** | Public, or shared with `GauthierFavier` |
| **`DESIGN.md`** | To understand how you used AI |
| **Loom video** | ≤ 3 min. Walk through your tool design and the trickiest edge case |

## Submission

Send to **gauthier@auditoo.eco**:

- Link to your GitHub repo
- Loom link

Good luck — we look forward to chatting with you!

ai-engineer.md
Displaying ai-engineer.md.
