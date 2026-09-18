# Survey: AI ingestion of verification artifacts

This survey examines prior work relevant to presenting physical-verification artifacts to
language-model agents. It is organised around the two overheads measured in our own KLayout
experiments (see `docs/results_phase2.md`): fixed report-level content that is irrelevant to
a particular debugging task, and repeated per-violation representation overhead. The question
is not only whether a representation is smaller, but whether it preserves the information a
debugging task actually needs.

Environment for all measurements quoted here: `docs/environment.md`.

---

## 1. KLayout report databases

KLayout represents DRC results in a Report Database. The native `.lyrdb` file is an XML
serialization of that object model, and it is designed to be viewed through the Marker
Browser. The marker workflow carries human-review state: categories, visited and waived
markers, tags, and optional attached images. The IHP SG13G2 DRC documentation reflects this
as well — every consumption path it documents is graphical, and its output section is
illustrated with screenshots of the Marker Browser.

KLayout also exposes a programmatic ReportDatabase API, which supports iteration over cells,
categories and items, and provides item counts globally or per cell and category. So an agent
does not necessarily have to consume the serialized XML to obtain basic report information.

The distinction worth drawing is that this is a traversal and access interface rather than a
debugging information model. Root-cause grouping, task-oriented filtering, spatial
aggregation and progressive disclosure would all have to be built above it.

Our measurements show why that matters. In one full-deck run, 830 rule categories were
serialized while only 12 contained violations — roughly 1.4% of the catalogue was relevant to
that report. At larger scales the repeated per-marker structure dominates instead: each
violation occupies twelve lines of XML of which one carries geometry, and 64–67% of each
marker's tokens are overhead rather than geometry, stable from 11 markers to 38,400.

The largest scale case contained **38,400 reported markers**, produced by repeating a base
cell carrying 24 markers across 1,600 identical instances, and the complete `.lyrdb` required
**4,468,961 tokens** under the reference tokenizer. This result is documented in
`docs/results_phase2.md`; whether those 24 markers correspond to 24 distinct root causes was
not separately verified. The repetition of identical marker patterns across instances is the
kind of redundancy that motivates comparing raw ingestion with semantic restructuring and
query-based access.

The human-oriented report representation and the information requirements of an LLM debugging
task are therefore not equivalent.

One consequence is directly relevant to the interface strategy: a per-rule count obtained
through `num_items` costs almost nothing, while the same information read from the file costs
the full report — up to 4.47M tokens in our largest case.

---

## 2. Generic document conversion: MarkItDown

MarkItDown is a general-purpose utility that converts documents to Markdown for LLM and
text-analysis pipelines, aiming to preserve structure such as headings, lists, tables and
links. It carries no domain knowledge of verification artifacts.

On a KLayout marker database it produced no reduction at all. A 49,392-token `.lyrdb`
remained 49,392 tokens after conversion, and the same file renamed to `.xml` gave an identical
result, so the file extension was not the barrier. The XML was returned unchanged, and no
error or warning was raised. Neither the unused rule catalogue nor the per-marker overhead was
removed.

This does not show that generic document conversion is ineffective in general. It shows
something narrower and more useful: a generic document transformation does not identify which
parts of a DRC artifact are relevant to a debugging task. Even a converter that handled the
format would have no basis for knowing that 826 of 830 rule descriptions are irrelevant to a
given report, or that `<value>` carries geometry while `<visited>` carries GUI state.

The silent no-op behavior is itself worth noting: a flow that passed DRC results through a
generic converter could incur the full token cost while appearing to have performed a
preprocessing step.

---

## 3. Token-oriented serialization: TOON

TOON is a compact, lossless encoding of the JSON data model intended for LLM input. It
combines indentation-based structure with a CSV-style tabular layout for uniform arrays,
declaring the field list once and then streaming one row per record. The project reports comparable retrieval accuracy while using 42.6% fewer tokens than
formatted JSON on its benchmark.

TOON does not read tool output; it encodes JSON. A parser must first extract records from the
report, which makes this a serialization layer rather than an ingestion layer.

We compared three forms of the same violations, extracting `{rule, cell, geometry}` records:

| Report | Raw XML | Compact JSON | TOON | TOON vs JSON |
|--------|---------|--------------|------|--------------|
| 4 markers | 49,392 | 177 | 161 | 9.0% |
| 7,680 markers | 897,638 | 418,565 | 372,494 | 11.0% |

The result separates two effects. Discarding rules that did not fire and dropping GUI
bookkeeping produced the dominant saving; replacing JSON with TOON gave a further 9–11% on
this data, compared with the 42.6% reduction relative to formatted JSON reported by TOON on
its own benchmark.

The reason is structural, and the TOON documentation anticipates it: savings come from
declaring field names once, so they are largest when field names are a large share of the
text. Our records carry three short field names and one long quoted geometry string of 30+
tokens, leaving little syntax to compress.

The remaining cost is semantic rather than syntactic. In the off-grid report, each marker
spends roughly 48 tokens on a degenerate edge-pair that repeats the same coordinate four times
in order to say that one vertex is off grid — and 7,680 such markers describe a single root
cause. No serializer addresses that.

For DRC artifacts, then, deciding *what* information to present matters more than choosing a
more compact syntax for the same information.

---

## 4. Model Context Protocol

MCP standardizes how AI applications access tools, resources and structured data, and current
versions support structured tool results with declared output schemas. It is a plausible
substrate for query-based access to a violation database: the specification's own worked
example is a database server exposing query tools, a schema resource, and prompts for using
them.

What MCP does not supply is any EDA-specific content. It does not define a violation data
model, decide how violations should be grouped, determine what spatial context should
accompany a marker, specify how repeated violations should be aggregated, or say when an agent
should receive a summary rather than full geometry.

MCP answers how an agent can query something through a standard protocol. This project asks
what a DRC server should expose and how that information should be organised. An interface for
this domain might offer operations such as listing rules with violations, returning counts per
rule, fetching a single violation, retrieving violations near a region, or proposing clusters.
MCP could transport those calls; whether that access model outperforms raw ingestion or a
restructured file is an empirical question, and one this benchmark is built to answer.

---

## 5. ChatEDA

ChatEDA is an LLM-driven agent for EDA in which a fine-tuned model, AutoMage, decomposes
natural-language requirements, generates scripts, and executes operations through programmatic
interfaces, primarily over OpenROAD. Its contribution is autonomous orchestration of the
RTL-to-GDSII flow, and its evaluation grades planning and script generation.

Tool output does re-enter its loop. Its API exposes a `get_metric` function, and a clock-period
optimization case retrieves the final WNS and adjusts the design parameter accordingly. So
selected numerical results can be returned through a programmatic metric interface and used in
closed-loop optimization.

What it does not address is the representation of large verification artifacts. It does not
study how a DRC marker database should be encoded, summarized, clustered or queried, does not
compare alternative output representations, and does not measure debugging success against
artifact-ingestion cost.

The two research questions are distinct. ChatEDA asks whether an LLM can orchestrate EDA
tools. This work asks what information an agent should receive once verification has produced
a large debugging artifact, in what representation, and at what cost.

---

## 6. Agentic EDA literature

The Agentic EDA survey organises autonomous design systems around a Perception–Cognition–Action
stack and frames the field as a constrained neuro-symbolic optimization problem rather than
"chat with tools". Its perception discussion concerns representing heterogeneous circuit
modalities — RTL, netlists, layout geometry — as multimodal embeddings, and it treats reading
tool output as part of the agentic loop.

Most relevant here, it identifies fragmented tool interfaces and fragile, tool-specific text
parsing as barriers to trustworthy autonomy, and argues that future interfaces should expose
tool state through structured, machine-readable APIs rather than raw log text. Its
future-directions discussion also raises inference economics, suggesting that benchmarks report
wall-clock efficiency alongside token cost.

This positions the survey as supporting evidence that the problem matters, not as work that
overlooks it. What remains open is the empirical question. The survey does not quantify the
context cost of existing verification artifacts, does not evaluate DRC debugging success under
alternative representations, and does not compare raw ingestion, serialization, semantic
restructuring and query-based access under common ground truth.

---

## Gap

Prior work supplies several pieces of the solution without evaluating the ingestion problem
itself. KLayout provides both a human-oriented report database and programmatic access to its
contents. Generic document transformation and token-oriented serialization offer general
methods for reducing representation overhead. Agentic EDA systems demonstrate tool
orchestration and the use of selected tool feedback, and recent surveys explicitly call for
structured EDA interfaces. MCP provides a protocol through which such interfaces could be
exposed.

To the best of our knowledge, we have not identified prior work that establishes how DRC
verification artifacts should be presented to language-model agents, or that measures how that
choice affects debugging performance. In particular, we have not identified a benchmark that
evaluates raw report ingestion, syntactic compression, semantic restructuring and query-based
interface access on the same ground-truth DRC debugging tasks, while reporting task success,
token usage, cost and latency across report scale and model choice.

This work addresses that gap by constructing a reproducible ground-truth DRC debugging corpus
and evaluation harness, and using it to compare those strategies against the raw artifact
baseline.

---

## Sources

1. KLayout, **RDB Format** — description of the `.lyrdb` XML report-database format and its
   relationship to the internal report-database object model:
   https://www.klayout.de/staging/rdb_format.html

2. KLayout, **Marker Browser** — documentation of report-database markers, tags, visited/waived
   state, geometry, and images:
   https://www.klayout.org/downloads/master/doc-qt4/manual/marker_browser.html

3. KLayout, **ReportDatabase API Reference** — programmatic access to report-database cells,
   categories, items, and `num_items` counts:
   https://www.klayout.org/downloads/master/doc-qt5/code/class_ReportDatabase.html

4. IHP GmbH, **IHP Open PDK** — public SG13G2 process design kit, KLayout DRC deck, and
   regression infrastructure used for the benchmark:
   https://github.com/IHP-GmbH/IHP-Open-PDK

5. Microsoft, **MarkItDown** — general-purpose document-to-Markdown conversion utility for LLM
   and text-analysis pipelines:
   https://github.com/microsoft/markitdown

6. TOON Format, **Token-Oriented Object Notation (TOON)** — implementation, rationale, and
   token-efficiency benchmarks:
   https://github.com/toon-format/toon

7. TOON Format, **TOON Specification** — formal syntax and data-model specification:
   https://github.com/toon-format/spec

8. Model Context Protocol, **Specification** — standard protocol for exposing tools, resources,
   prompts, schemas, and structured results to AI applications:
   https://modelcontextprotocol.io/specification

9. He et al., **ChatEDA: A Large Language Model Powered Autonomous Agent for EDA**,
   *IEEE Transactions on Computer-Aided Design of Integrated Circuits and Systems*,
   43(10):3184–3197, 2024. arXiv:2308.10204.
   https://arxiv.org/abs/2308.10204

10. Zang et al., **The Dawn of Agentic EDA: A Survey of Autonomous Digital Chip Design**,
    arXiv:2512.23189, 2025.
    https://arxiv.org/abs/2512.23189
