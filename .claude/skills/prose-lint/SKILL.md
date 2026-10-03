# Prose lint

Audit prose against [.claude/rules/prose.md](../../rules/prose.md) and apply the fixes.

Read that rules file in full before the first edit. This skill describes the procedure only; the
rules file is the authority on what is banned.

Audit adversarially. When a sentence is defensible under a loose reading and a violation under a
strict one, treat it as a violation. A borderline construction is rewritten, not excused, and doubt
resolves toward the edit. Under-reporting is the failure mode to avoid. A grep hit stands until you
can state which exemption in this file covers it.

## Scope

### Default target

Audit files with pending changes, from `git status --porcelain` and `git diff --name-only HEAD`.
When the user gives paths or a diff range, use those instead.

Audit every piece of prose inside each target file:

- Markdown body text, including headings, list items, table cells, and admonitions.
- Plain comments in any language.
- Formal documentation comments (Numpydoc, JSDoc, Doxygen, Javadoc, XML doc comments). The same
  standard applies to them as to Markdown body text.
- User-facing string literals such as log messages, help text, error messages, and CLI output.
- Commit messages under review.

Do not edit:

- Identifiers, code, URLs, file paths, and dependency names.
- Assistant instructions. `AGENTS.md`, `CLAUDE.md`, and everything under `.claude/` are out of
  scope, including when the user requests every file (`everywhere`, `the whole repository`, a
  glob that covers them). Report a hit in one of them only when the user has requested a change to
  that file.
- Fenced blocks and italic examples inside `.claude/rules/prose.md`. They exist to demonstrate
  violations.
- Released `CHANGELOG.md` sections. Only the `Unreleased` section is in scope.
- Quoted material from an external source. Flag it for the user instead.

## Detection

Run the greps below over the target files, then review every hit by hand. Each grep over-matches by
design; a noun matching a banned verb is valid, and the fix depends on the sentence. _claim_ is
valid wherever a specification defines it as a term, such as an OIDC or JWT claim. The noun
_project_ is valid and accounts for most hits on that word. Only the verb is banned, and the
geometric sense of the verb is valid too. The noun _ask_ is banned as well. Review every hit on that
word rather than excusing the noun.

```shell
grep -nP '\x{2013}|\x{2014}' <files>
```

```shell
grep -nEi "[[:alpha:]]+n[’']t\b|[[:alpha:]]+[’'](re|ll|ve|m)\b|\b(it|that|there|here|let|what|who)[’']s\b" <files>
```

```shell
grep -nEiw "gate|gates|gated|gating|stamp|stamps|stamped|stamping|answer|answers|answered|answering|say|says|said|saying|spell|spells|spelled|spelling|state|states|stated|stating|contain|contains|contained|containing|carry|carries|carried|carrying|hold|holds|held|holding|keep|keeps|kept|keeping|reach|reaches|reached|reaching|name|names|named|naming|title|titles|titled|titling|lay|lays|laid|laying|leave|leaves|left|leaving|confine|confines|confined|confining|manufacture|manufactures|manufactured|manufacturing|mint|mints|minted|minting|claim|claims|claimed|claiming|ask|asks|asked|asking|transport|transports|transported|transporting|project|projects|projected|projecting|bake|bakes|baked|baking|null|nulls|null(ed|ing)|own|owns|owned|owning" <files>
```

```shell
grep -nEi "\banyway\b|\banyone\b|\bnobody\b|\bno[ -]?one\b|\bobligatory\b|straight[ -]up|ground truth|house style|house convention|elephant in the room|writing on the wall|beat around the bush|best[ -]of[ -]breed|call it a day|cut to the chase|hit the nail on the head|jump on the bandwagon|think outside the box" <files>
```

Ornamental wording and filler need a pass of their own. Delete a hit that adds no fact a reader
cannot already derive, and retain one that changes the meaning. _actor_ is valid wherever a
specification defines it as a term. _leading_ is valid in the positional sense (_a leading zero_,
_leading whitespace_), and banned as an adjective of rank or prominence.

```shell
grep -nEiw "leverage|leverages|leveraged|leveraging|sunset|sunsets|simply|just|basically|various|powerful|seamless|robust|actor|actors|leading" <files>
```

```shell
grep -nEi "it is worth noting|in order to" <files>
```

```shell
grep -nEi ", (which|so|since|because)\b|says nothing|say nothing|for such|left alone|written by hand|that matters is|\b[[:alpha:]]+s no\b|\b(give|make|take|need|want|hold|know|find|show|draw|add|read|write|identify|record|list|store|specify|use|mark) no\b|\bstate[sd]\b|\bsomething\b|\bnothing\b|of (its|their|his|her) own|their own" <files>
```

Personification hits, an inanimate subject taking a verb of life or emotion (a noun of the same
spelling is valid, such as a `die` roll or a `wish` list):

```shell
grep -nEiw "survive|survives|survived|surviving|die|dies|died|dying|perish|perishes|perished|perishing|breathe|breathes|breathed|breathing|suffer|suffers|suffered|suffering|wish|wishes|wished|wishing|enjoy|enjoys|enjoyed|enjoying|hope|hopes|hoped|hoping|fear|fears|feared|fearing" <files>
```

Headings and titles need a separate pass:

```shell
grep -nE "^#{1,6} (The|What|Which|Whose)\b" <files>
```

```shell
grep -nEi 'either[.,;:!?)]*$' <files>
```

```shell
grep -nE "[a-z][a-z)\`_]: +[a-z]" <files>
```

```shell
grep -nE "\b(Ascii|Nasa|Nato|Unesco|Html|Css|Url|Api|Cli|Json|Yaml|Ssh|Http|Xml|Sql)\b" <files>
```

A colon that introduces a list of items is valid. Review each hit. A colon followed by a clause is
the banned form, and the only permitted elaboration is a second sentence opening with _That is,_.

Two patterns need a read pass rather than a grep. Headings take the gerund-plus-pronoun form
(_Pointing an agent at it_), and body text substitutes _that_, _this_, _these_, or _those_ for a
noun already available. A grep over the demonstratives over-matches so heavily as to be useless.
Every restrictive clause and every legitimate determiner hits.

## Fixing

1. Rewrite each confirmed hit in place with `Edit`. Preserve the meaning, the wrap width of the
   surrounding file, and the existing indentation.
2. Prefer deletion. A trailing justification clause, a vague follow-on sentence, and a
   _(number) things worth ...:_ preamble are all removed rather than reworded.
3. A banned verb usually disappears with the sentence restructured, not with a synonym dropped into
   the same slot. Verify the replacement reads naturally.
4. Re-wrap any paragraph whose length changed, at the width the file already uses (100 characters
   for Markdown and Python in this repository).
5. Never alter code, identifiers, or test expectations to make prose fit. When a string literal is
   asserted in a test, update the test in the same edit.

## Verification

Run both commands and confirm exit code 0:

```shell
yarn format
```

```shell
yarn qa
```

Then re-run the detection greps. Report the remaining hits with a one-line justification each, or
report a clean result.

## Reporting

Give the user a short list of file, line, banned pattern, and the fix applied. Group by file. Do not
add a summary paragraph beyond the list.
