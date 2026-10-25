# VoiceOps Evaluation ? Preliminary Results

Dataset: 52 questions
Evaluation method: automated must_include / must_not_include phrase checks

| Metric | LLM-only | RAG |
|---|---:|---:|
| Total questions | 52 | 52 |
| Completed answers | 17 | 15 |
| API/processing errors | 35 | 37 |
| Phrase-check passes | 6 | 7 |
| Pass rate among completed answers | 35.3% | 46.7% |

## Interpretation

RAG achieved a preliminary phrase-check pass rate 11.4 percentage points
higher than the LLM-only baseline among completed answers.

These results are inconclusive: 35 LLM-only requests and 37 RAG requests
failed, primarily because of API rate limits. Phrase checks are a proxy,
not a full measure of factual correctness or groundedness. A fair comparison
requires rerunning failed questions and reviewing answer quality against
the reference answers and evidence sections.

Do not present these preliminary rates as final accuracy scores.
