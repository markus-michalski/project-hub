---
name: meeting-prep
description: |
  Prepare a structured agenda before a meeting, distinguishing recurring vs. one-off and
  internal vs. external meetings, with each agenda item anchored to its relevant file(s)/
  source(s) and a short context description — so "which file was this about again?" doesn't
  happen mid-meeting.
  Use when: user wants to prepare for an upcoming meeting, says "Meeting vorbereiten",
  "Agenda erstellen", "prepare for meeting", "meeting prep", `/project-hub:meeting-prep`.
  Do NOT trigger on a bare "Meeting" mention without explicit prep/agenda intent — could just
  be logging notes (`add-note`) or summarizing one after the fact (`summarize`).
model: claude-sonnet-4-6
user-invocable: true
argument-hint: "[Meeting-Titel]"
---

# Meeting Prep

Prepare a structured agenda for an upcoming meeting — each item anchored to its relevant
file(s)/source(s) and a short context note, so recall doesn't depend on memory across many
parallel projects.

## Workflow

### 1. Context

Use MCP `tool_get_session()` (returns a bare `dict`, always — not wrapped). Read the
**`project_id`** field, not `id` — `id` is the session row's own primary key (always `1`, per
`tools/session.py`'s single-row table) and is truthy even with no active project, while
`project_id` is `null`/absent in that case. Also note `project_name` from the same response; both
are needed unchanged in Step 4 and Step 6 — no second session call.

If a `[Meeting-Titel]` argument was provided, use it as the working title; otherwise ask: "Wie
heißt das Meeting bzw. worum geht's?". Then ask for the meeting date ("Wann findet das Meeting
statt?", default: today if the user has no specific date yet) and fold it into the working title
the same way `add-note` recommends (e.g. "Weekly Sync 2026-09-22") — this avoids same-day/
same-title notes overwriting each other's on-disk file later (Step 6) and gives the rendered
agenda a date to show.

Having an active project is only a default suggestion for Step 6's "file under" question, not a
requirement — agenda-building in Steps 2-5 works with or without one.

### 2. Meeting-Typ

Use `AskUserQuestion` (two questions in one call):
- "Wiederkehrend oder einmalig?" — **Wiederkehrend** / **Einmalig**
- "Intern oder extern (nimmt jemand außerhalb der Organisation teil)?" — **Intern** / **Extern**

Do not try to derive this from who's attending — ask directly. This deliberately keeps the
skill from loading any contact/attendee data at all, and matches the point of asking: a direct
human call, not an inference.

If "Wiederkehrend" and a `project_id` is known (from Step 1, or resolved in Step 4's search):
before starting Step 4's collection loop, run `tool_search_notes(<Kernwort aus dem Titel>,
project_id=<project_id>)` (see Step 4 for the exact wrapping/unwrap rule) and filter the results
client-side to `type == "meeting-notes"`. If a prior occurrence turns up, offer its rendered
agenda text back to the user and ask which items (if any) are still open and should carry
forward into this one — accepted items seed Step 4's loop, they don't replace it. Skip silently
if nothing matches; this is a convenience, not a requirement.

### 3. Agenda-Tiefe

Use `AskUserQuestion` with exactly these two option labels (reused verbatim in Steps 5 and 7 —
do not rephrase them there):
- **Nur die dringlichsten Punkte** (description: "kurz, fokussiert" — add ", empfohlen für
  wiederkehrende/interne Meetings" when Step 2 was Wiederkehrend+Intern)
- **Vollständiger Überblick** (description: "vollständige Liste" — add ", empfohlen für
  einmalige/externe Meetings" when Step 2 was Einmalig+Extern)

Put the recommendation in the option's **description**, not appended to the label — any other
combination of Step 2's answers gets no recommendation, present both plainly.

### 4. Agendapunkte sammeln

Loop until the user says they're done (starting from any carried-forward items accepted in Step
2). For each new item, ask:
- **Titel** — kurzer Themenname
- **Kontext** (1-2 Sätze) — worum geht es, was ist das gewünschte Ergebnis (Entscheidung /
  Input / nur FYI)
- **Dringlich?** (ja/nein) — immer fragen, unabhängig von der in Step 3 gewählten Tiefe; wird
  in Step 5 zum Filtern gebraucht
- **Quelle(n)** (optional) — Dateipfad(e), auf die sich der Punkt bezieht

Before asking the user to recall a source from memory, proactively offer a search: run MCP
`tool_search_notes(query, project_id=<project_id from Step 1, or the project resolved so far>)`
using the item's title/keywords. Its return annotation is `list[dict]`, so per the
response-wrapping rule the result is wrapped — read `response["result"]` (a list of note dicts,
each with `project_name`, `title`, `id`, ...), not `response["items"]`. If nothing is found, or no
`project_id` is known yet, ask "Auch in allen anderen Projekten suchen?" before widening to
`project_id=0` — mirrors `search`'s scope-question rule instead of defaulting to an all-projects
read of other clients' full note content. Present likely matches; let the user pick one, skip, or
give a path manually. If the search (scoped or widened) returns nothing, say so plainly and move
on to manual entry — don't imply a match was checked when none was found.

If Step 2's answer was "Extern": before including any source — including one just found via
search — ask "Ist [Quelle] für externe Teilnehmer geeignet?" — a conversational checkpoint, not a
technical filter (project-hub has no file-level confidentiality flag). Leave the source out if
the answer is no. Ask this regardless of whether the source came from search or was typed
manually — the checkpoint is about what goes into an externally-relevant agenda, not about how
the source was found.

Ask "Weitere Punkte?" after each item; stop on "nein"/"fertig"/no more items.

### 5. Agenda rendern

Render the agenda as Markdown, one block per item:

```
### N. <Titel>
**Kontext:** <Kontext-Text>
**Quelle:** <Pfad(e) oder "–">
```

Branch on Step 3's exact option label (do not introduce a third spelling here or in Step 7):
- "Nur die dringlichsten Punkte": include only items marked dringlich in Step 4 (renumber
  sequentially). If none were marked dringlich, include all items anyway and say so plainly
  rather than emitting an empty agenda.
- "Vollständiger Überblick": include all items in collection order.

### 6. Speichern

Ask "Unter welchem Projekt ablegen?" — default to the `project_id`/`project_name` pair from Step
1 if one exists (confirm the resolved project *by name*, don't save silently under it). Without
an active project, resolve via `tool_list_projects()` (bare `dict`, read `response["items"]`;
each row's `id` field is the `project_id` to use below) the same way `resume`'s find-project step
does.

If the user wants to save: call `tool_add_note(project_id, title=<Titel inkl. Datum aus Step 1>,
content=<rendered Markdown from Step 5>, note_type="meeting-notes", agenda=<the same rendered
Markdown>)` — pass the identical rendered text to **both** `content` and `agenda`. This matters
beyond just the on-disk docs mirror (`tools/notes.py` writes it from `content` only): the
project's cross-project search (this skill's own Step 4) and the HTML report both read `content`,
never `agenda` — an empty `content` would make the saved agenda invisible to both, defeating the
point of writing it down at all. `agenda` stays there too so `/summarize`'s post-meeting
Agenda-Abgleich keeps working exactly as before. `tool_add_note` returns a bare `dict` (not
wrapped) — read the `id` field directly from the result, never `result["result"]["id"]`.

Offer `tool_attach_file(note_id, file_path)` only for sources the user explicitly wants
preserved verbatim — not the default for every mentioned source, see Notes below. If offered:
the path must be fully expanded and absolute under the user's home directory —
`tool_attach_file` does **not** expand `~`, so a literal `~/Documents/spec.pdf` fails with a
misleading "File not found" instead of a path-traversal error. Expand `~`-prefixed or relative
paths yourself before calling it (same gotcha `add-note` documents).

If the user doesn't want to save (no relevant project yet, or they just want the text now): skip
this step — the rendered agenda from Step 5 is already fully usable standalone.

### 7. Output

```
## Meeting-Agenda: [Titel]

**Typ:** [Wiederkehrend|Einmalig] / [Intern|Extern]
**Tiefe:** [Nur die dringlichsten Punkte|Vollständiger Überblick]

[rendered agenda from Step 5]

[Gespeichert als Notiz-ID: [id] im Projekt [Projektname]] (nur wenn gespeichert)
```

If saved, add this footer:
```
Tipp: Nach dem Meeting `/project-hub:edit-note [id]` für die tatsächlichen Notizen, danach
`/project-hub:summarize [id]` für den Agenda-Abgleich.
```

## Notes

- No new MCP tool or schema needed — this reuses the existing `agenda` field on `meeting-notes`
  (already read back by `/summarize`'s Agenda-Abgleich step) plus `tool_search_notes` for
  cross-project recall. The agenda is written to `content` as well so search and reports can see
  it (see Step 6) — `agenda` alone is not enough for either.
- Sources are path mentions inside the agenda text, not `tool_attach_file` copies by default —
  attaching is for the rare case a document must be preserved verbatim, not the standard way to
  say "this is what the item refers to."
- The external-meeting confidentiality checkpoint in Step 4 is conversational, not a technical
  filter — project-hub has no file- or note-level confidentiality flag today. A real structural
  flag would be future work, not part of this skill.
- Cross-project search (Step 2's carry-forward check, Step 4's per-item search) defaults to the
  known project and only widens to all projects on explicit confirmation — matching `search`'s
  own scope-question rule, not a blanket `project_id=0` read of every client's notes.
