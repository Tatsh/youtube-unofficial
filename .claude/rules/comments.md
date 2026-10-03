---
name: comments
description: 'Comments need to be to the point and serve a purpose.'
---

# Comments

If you are considering whether or to write a comment, check if the comment passes this test:

Does it say something the code genuinely cannot — a non-obvious _why_, a subtle edge case, a
business rule invisible locally, or a workaround?

Do _not_ write it if it restates the code, labels obvious structure (`# imports`, `# helper`),
announces a phase (`// Step 1: validate`), draws a decorative separator, summarises the function it
sits above, narrates the block below it, describes the edit itself (`// changed from`,
`// now handles`, `// new`), or is commented-out code. Also delete it if the surrounding file
deliberately has none — match the file's existing comment density rather than raising it.

Doc comments (docstrings, etc) follow the file's convention and cover the public surface only.
Document behaviour, invariants, units, and error conditions.

If a correction is being made, a comment mentioning the prior state is not worth having because the
commit message mentioning why the change was made will suffice.

Comments must stay true on any machine: never mention this sandbox, host, or session.
