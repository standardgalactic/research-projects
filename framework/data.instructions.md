---
applyTo: "data/**"
---

# Data instructions

- Treat source data as evidence, not as convenient mutable input.
- Every record includes `source`, `source_locator`, `retrieved`, `origin`, `transformation`, `certification`, `boundary`, `unit`, and `assumptions` where applicable.
- Prefer primary papers, supplements, repositories, manuals, and data sheets. Use a retailer or secondary summary only when no primary source is available, and label that limitation.
- Record exact article versions, repository commits, file hashes, table cells, figure panels, notebook cells, and data ranges whenever available.
- Keep raw, normalized, and generated data in separate locations. Never edit raw data to simplify a parser.
- Normalization code must be reproducible and preserve a mapping back to every original field.
- Unknown values remain unknown. Do not encode missing power, time, precision, or boundary as zero.
- Do not infer a device boundary from a component name or a system boundary from a paper title.
- Preserve significant figures as reported while retaining exact parsed values when the source permits them.
- Do not relicense third-party data. Retain license and attribution metadata.
- Schema changes require migration notes and tests against existing records.

