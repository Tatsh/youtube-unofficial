# Prose guidelines

These rules cover every piece of prose produced for this repository: Markdown, commit messages,
review notes, plain comments, user-facing string literals, and formal documentation comments in any
format (Numpydoc, JSDoc, Doxygen, Javadoc, XML doc comments, and equivalents). A formal comment
format is no exemption. Code, identifiers, URLs, and file paths are exempt.

Assistant instructions are exempt as well. `AGENTS.md`, `CLAUDE.md`, and everything under
`.claude/` are never rewritten to satisfy these rules, whether by a lint pass or in passing during
other work. Edit them only when the user requests a change to them.

Text shown to a non-developer end user is exempt and is never rewritten to satisfy these rules.
This covers website copy and application UI text (labels, buttons, headings, in-app messages).
Command-line text is not exempt: help strings, usage output, command results, and error messages
presented at a terminal follow every rule here. Edit end-user product copy only when the user
requests a change to it.

Apply these rules adversarially. A construction that is defensible under a loose reading and a
violation under a strict one is a violation, and doubt resolves toward the rewrite.

Examples of banned writing appear in italics or inside a fenced block. Linting must skip them.

## Punctuation

- Contractions are banned. Write _do not_, _cannot_, _it is_, _there is_, _you will_.
- En dashes (_–_) and em dashes (_—_) are banned in every position. Rewrite with a comma, a colon, a
  semicolon, parentheses, or a full stop.
- A sentence must never finish with a dash plus a trailing remark. Delete the remark or promote it
  to a full sentence of its own.
- Hyphens remain valid inside compound words (_hand-written_, _pre-commit_, _read-only_).
- Do not attach an elaboration to a statement with a colon. _Properties with no timestamp are
  exempt: no timestamp means no record of the choice_ becomes two sentences. A colon introducing a
  list of items remains valid. The one permitted elaboration is a second sentence opening with
  _That is,_.
- A label followed by a colon is banned (_Default target:_, _Exceptions:_, _Note:_). In Markdown,
  promote the label to a heading. Elsewhere, fold the label into the sentence.

## Acronyms and abbreviations

- Write an acronym in full uppercase, whether a reader pronounces it as a word or reads it out
  letter by letter. _ASCII_, _NASA_, _NATO_, _UNESCO_, _HTML_, _URL_, and _JSON_ all take the same
  treatment.
- An entity whose common usage differs takes its own form. _Ofcom_ is the UK regulator, and _OFCOM_
  is the Swiss federal office. Follow common usage for the specific entity rather than a general
  pattern.
- Product and vendor spellings follow the vendor, such as _macOS_, _iOS_, _GitHub_, _PyPI_, _npm_,
  _FFmpeg_, and _D-Bus_.

## Banned verbs

Every inflection of each verb below is banned (_says_, _said_, _saying_, _keeps_, _kept_, and so
on). A noun or adjective of the same spelling is allowed. _The name of the file_ and _a rubber
stamp_ are both fine. _spell-check_ is allowed in every form and position. _claim_ is allowed
wherever a specification defines it as a term, such as an OIDC or JWT claim. _state_ is allowed as a
noun (_a state machine_, _the saved state_) and inside _restate_, and no replacement in this table
is itself a banned verb. _name_ is allowed in the passive form that describes where a name comes
from, such as _the file is named after the archive_ and _the directory named after it_. _null_ is
banned as a verb, and _nullify_ is allowed, as are the noun and adjective (_a null value_, _the
column is null_). _project_ is banned wherever _display_ fits. The geometric sense of mapping a
point or a shape onto a surface or an axis is allowed (_project the vertex onto the near plane_),
and so is the noun _projection_. _ask_ is banned as a noun as well (_the ask_, _a big ask_, _the
asks for this quarter_). Write _request_.

| Banned        | Write instead                       |
| ------------- | ----------------------------------- |
| _answer_      | _respond, reply, resolve_           |
| _ask_         | _request, query, prompt_            |
| _bake_        | _embed, build in, compile in_       |
| _carry_       | _include, have, move_               |
| _claim_       | _assert, report, record_            |
| _confine_     | _limit, restrict_                   |
| _contain_     | _include, list, comprise_           |
| _gate_        | _block, restrict, require approval_ |
| _hold_        | _store, include, have_              |
| _keep_        | _retain, preserve_                  |
| _lay_         | _place, put, set down_              |
| _leave_       | _depart, exit, abandon, omit_       |
| _manufacture_ | _produce, fabricate, build_         |
| _mint_        | _create, issue, generate_           |
| _name_        | _identify, specify, list_           |
| _null_        | _nullify, clear, unset, reset_      |
| _own_         | _provide, include, manage_          |
| _project_     | _display, show, forecast_           |
| _reach_       | _arrive at, contact_                |
| _say_         | _write, document, report, record_   |
| _spell_       | _write, writes, reads_              |
| _stamp_       | _mark, write, record_               |
| _state_       | _record, specify, report, require_  |
| _title_       | _identify, label, call_             |
| _transport_   | _move, ship, deliver_               |

## Banned words and phrases

- _anyone_
- _anyway_
- _beat around the bush_
- _best-of-breed_
- _call it a day_
- _cut to the chase_
- _elephant in the room_
- _ground truth_
- _hit the nail on the head_
- _house convention_
- _house style_
- _jump on the bandwagon_
- _no one_, _no-one_, and _noone_
- _nobody_
- _obligatory_
- _straight-up_ and _straight up_
- _the writing on the wall_
- _think outside the box_

_leading_ is banned as an adjective of rank or prominence (_the leading provider_, _an
industry-leading tool_, _a leading cause_). Give the concrete fact instead, or delete the word. The
positional sense of first in a sequence is allowed (_a leading zero_, _leading whitespace_, _a
leading underscore_).

## Personification

An inanimate subject does not take a verb reserved for a living thing. A file, a byte, a record, a
chart, a value, a path, or a character does not _survive_, _die_, _perish_, _live_, _breathe_,
_wake_, _sleep_, _suffer_, _feel_, _care_, _enjoy_, _wish_, _hope_, or _fear_. This list is not
comprehensive. Any verb of life, death, sensation, or emotion is banned for an inanimate subject,
whether or not it appears here. Rewrite with the mechanism. _the fallback fires when no character
survives_ becomes _the fallback fires when no character remains_, and _a byte that dies_ becomes _a
byte that is discarded_.

An active component described as an agent is exempt for verbs of action and cognition, not of life
or emotion. _the parser expects a header_ and _the reader knows the offset_ are allowed. _the parser
is happy_ and _the reader grows tired_ are not.

## Banned phraseology

| Banned pattern                                                                     | Fix                                                                                                                                                                                                |
| ---------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| _they say nothing about X_, _it says nothing about X_, _that says nothing about X_ | Record what is absent, or delete the sentence.                                                                                                                                                     |
| _X verbs no Y_, such as _the pass touches no files_                                | Rewrite as _X does not verb Y_, such as _the pass does not touch files_.                                                                                                                           |
| _nothing verbs Y_, such as _nothing touches the page_                              | Identify the subject and negate the verb, such as _the page is never written to_. Where the subject is genuinely every candidate, _no X verbs Y_ is the rewrite.                                   |
| _X states that Y_ and _X states Y_, such as _the rule states that tests pass_      | Rewrite as _X requires Y_ where X imposes the requirement, and as _X records Y_ or _X specifies Y_ where X merely reports it.                                                                      |
| _..., which (second statement)_                                                    | Delete the clause by default. A reader derives an obvious consequence, restatement, or justification without it. Split into two sentences only when the clause adds a fact a reader cannot derive. |
| _..., so (second statement)_ and _..., so that ..._                                | Delete the clause by default. A reader derives an obvious consequence, restatement, or justification without it. Split into two sentences only when the clause adds a fact a reader cannot derive. |
| _..., since (second statement)_                                                    | Delete the clause by default. A reader derives an obvious consequence, restatement, or justification without it. Split into two sentences only when the clause adds a fact a reader cannot derive. |
| _for such_                                                                         | Rewrite with the concrete noun.                                                                                                                                                                    |
| _left alone_                                                                       | Specify the concrete action, for example _no edit was made_.                                                                                                                                       |
| _written by hand_                                                                  | _hand-written_                                                                                                                                                                                     |
| _(number) things worth (verb):_                                                    | Delete the preamble and give the items.                                                                                                                                                            |
| _... that matters is ..._                                                          | State the item directly.                                                                                                                                                                           |
| _, because (vague justification)_ at the end                                       | Delete the clause.                                                                                                                                                                                 |
| _either_ at the end of a sentence                                                  | Delete the word, or restructure the sentence.                                                                                                                                                      |

## Specificity

- Write plainly. Prefer the plain word to the ornamental one (_use_ over _leverage_, _end_ over
  _sunset_, _let_ over _enable_ where the meaning is _let_). State the mechanism directly rather
  than through an abstract stand-in. A phrase such as _the audited layer that lets_ names nothing
  concrete. Write what the code actually does.
- Prefer _user_ to _actor_ for the person who performed an action, unless a specification defines
  _actor_ as a term.
- De-fluff. Delete a word, clause, or sentence that adds no fact a reader cannot already derive.
  Adjectives and adverbs that do not change the meaning (_simply_, _just_, _basically_, _various_,
  _powerful_, _seamless_, _robust_), throat-clearing openers (_it is worth noting that_, _in order
  to_), and a sentence restating the previous one all go. Shorter is correct when nothing is lost.
- Do not write _something_ where a specific noun exists.
- Do not use _that_, _this_, _these_, or _those_ as a stand-in for a noun already available. Repeat
  the noun. _that timestamp_ becomes _the global timestamp_, and _a folder in that state_ becomes
  the condition itself.
- Delete a definite article wherever the sentence survives without it. Proper names and generic
  plurals almost never take one. _the trash_, _the Downloads folder_, and _the special folders_
  become _trash_, _Downloads_, and _special folders_. Stacking articles across a sentence reads as
  padding.
- The same applies to _it_, _them_, _one_, and _none_ once a sentence offers more than one candidate
  noun. _retained every one of them_ becomes _retained its stored properties_. Where exactly one
  candidate noun exists, the pronoun is correct, and repeating the noun is padding.
- Delete possessive padding. _folders with no stored properties of their own_ becomes _folders with
  no stored properties_, and _their own default styles_ becomes _their default styles_.
- A short list of causes or examples belongs in parentheses inside the sentence it supports, rather
  than in a follow-on sentence. _Properties with no timestamp (old Dolphin, .directory with no
  timestamp) are exempt_ replaces a sentence enumerating both sources.
- Describe past behaviour in the past tense throughout a paragraph. _even when they predated the
  global timestamp_, not _even when they predate_.
- Do not report that a thing is present and then reveal what the thing is in the next sentence.
  Give the specific noun at first mention.
- Do not open a list with a fragment plus a justification. Write _These are the four statuses:_
  instead of:

  ```text
  Four statuses, because collapsing them loses the finding:
  ```

- One point per paragraph. After the point, delete every follow-on sentence that only restates why
  the point is true without adding a fact a reader can verify. Delete a sentence whose content a
  reader derives from the sentence before it. The paragraph below reduces to its first sentence:

  ```text
  The workload has to be the sandbox's own first process. That is measured, not stylistic: on the
  microVM tier a hook server started after the sandbox exists answers on the guest's loopback and is
  unreachable from the host, and the host cannot route to the guest address either — so nothing
  about the arrangement looks broken from inside.
  ```

- Vague justification at the end of a sentence is deleted, not rewritten. An example of what to
  delete:

  ```text
  ..., because an emulator whose divergence is invisible manufactures confidence instead of
  removing doubt.
  ```

## Headings and titles

- Do not begin a heading with _The_ (_The problem_, _The fix_).
- Do not begin a non-question heading with _What_ (_What this led to_, _What we found_).
- Do not begin a heading with a relative pronoun such as _Which_ (_Which leads to a rebuild_).
- Do not write a gerund heading whose object is a pronoun (_Pointing an agent at it_). Use a noun
  phrase with the concrete subject (_Agent configuration for the parser_).
