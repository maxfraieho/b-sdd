# Spec 003: Procedural Skill Lifecycle & The Rule of 2

## Objective
Establish the automated routing, alignment, and self-authoring lifecycle for agent skills within the B-SDD framework.

## Invariants
- Dynamic routing: active rules snapshot must always recommend skills based on active domains.
- The Rule of 2: operational patterns repeated >= 2 times must be proposed for crystallization into an agent skill.
- Standard metadata: all created skills must contain `SKILL.md` with YAML frontmatter.
