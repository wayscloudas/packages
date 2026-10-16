# Triage register — `wayscloudas/packages`

Every finding that is closed **without a fix** is argued here, one row per finding or per
rule-and-file pair. The reason has to name the consequence: not "looks fine", but what
can go wrong, for whom, and why not fixing it is acceptable.

Rules:

- A Sonar finding is **never** marked as a false positive in the Sonar UI. If a rule is
  genuinely wrong for this code, that is the reason recorded here, with a source
  reference (upstream commit, specification, or test).
- A rule-wide or repository-wide exception is not allowed. A
  `sonar.issue.ignore.multicriteria` entry is allowed only bound to **one rule and one
  resource pattern**, with the reason in `sonar-project.properties` and a row here.
- The register is append-only. A row that is no longer true gets a new row that says so.

| Date | Rule | Finding | Why it is not fixed | Consequence that was assessed | Reference |
|---|---|---|---|---|---|
| | | | | | |

*(No finding has been closed without a fix yet.)*
