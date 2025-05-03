# About this directory

Mypy is extremely slow when deeply nested dictionary literals are in code. This includes generic
non-typed dictionaries. To prevent Mypy from hanging or taking a long time to complete (more than 1
minute), complex dictionaries are placed in files here and loaded in the test with the `json`
module.

If adding a test that has a complex dictionary return value for a mock, add the JSON here and load
the data, making use of the `data_path` fixture.

If Mypy is slow to complete (more than a few minutes for all files), the likely reason is a complex
dictionary literal in the code.

Yapf is also very slow to format code with complex dictionary literals. This directory exists for
that reason as well.
