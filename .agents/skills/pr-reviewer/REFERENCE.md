# PR Reviewer — Reference

Quick lookup for common review patterns. Use during the review pass to ground findings in shared conventions.

## Common correctness issues

| Pattern | Problem | Preferred |
|---|---|---|
| Ignoring error return | Silent failure, wrong result propagated | Check and handle or explicitly propagate |
| Unchecked nil/null dereference | Runtime panic / null pointer exception | Guard before use or use optional types |
| Mutable default argument (Python) | Shared state across calls | Use `None` sentinel, initialise inside function |
| Catching broad exception (`except Exception`) | Hides unexpected failures | Catch specific exceptions; log unexpected ones |
| Unbounded retry loop | Runaway execution under failure | Add max-retries and backoff |

## Common reuse misses

| You see | Check first |
|---|---|
| Custom date parsing | stdlib `datetime` / `time` |
| Custom UUID generation | stdlib `uuid` |
| Custom HTTP retry logic | existing retry utility in the codebase |
| New logging setup | shared logging config already in the project |
| Hand-rolled base64 encode/decode | stdlib |

## Simplification signals

| Signal | What it usually means |
|---|---|
| Interface with one implementation | Remove the interface |
| Factory for one product | Inline the constructor |
| Config file for a value that never changes | Hard-code with a comment |
| Comment explaining what the code does | Rename the variable or function instead |
| Deep nesting (>3 levels) | Extract a function |
| Boolean parameter that changes behaviour | Split into two functions |
