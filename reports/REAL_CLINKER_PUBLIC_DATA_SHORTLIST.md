# Real Clinker Public Data Shortlist

## Scope and caution

This shortlist is intended as a preliminary public-source map only. It is not a claim that any listed source is a complete, production-linked clinker dataset. No automatic download or file integration was performed.

The purpose is to identify likely public sources that may require institutional verification before being used in a real clinker research workflow.

## Candidate 1 — NIST reference materials and cement-related analytical datasets

- Source: National Institute of Standards and Technology (NIST)
- DOI/URL: Confirm institutional material reference page and SRM catalog entry
- Sample count: Reference material lots, not a full plant production database
- XRF: Often available as reference characterization data
- XRD: Sometimes available for reference materials or method validation
- Rietveld: May be available for reference standards, but not necessarily full clinker process data
- Free CaO: Possible for selected reference materials, not a production dataset
- C3S/C2S/C3A/C4AF: Usually reference-style or method validation output, not a full kiln traceability table
- Process data: Not generally available
- Timestamps: Usually not production-time aligned
- Sample IDs: Reference material IDs; not production or kiln linkage keys
- Raw material data: Not a full raw-mix chain
- License: Institutional/public standards usage terms apply
- Track A suitability: No
- Track B suitability: Conditional, if measured phase analysis exists and is clearly traceable

## Candidate 2 — Public scientific supplementary tables from clinker or cement studies

- Source: Journal supplementary material / DOI-backed publications
- DOI/URL: Publication-specific DOI
- Sample count: Varies by paper; usually limited
- XRF: Frequently available
- XRD: Often available
- Rietveld: Sometimes available
- Free CaO: Sometimes available
- C3S/C2S/C3A/C4AF: Sometimes reported
- Process data: Usually not available
- Timestamps: Often absent or weakly structured
- Sample IDs: Paper-specific sample IDs only, not plant or kiln IDs
- Raw material data: Rarely available in a relational format
- License: Paper-specific license or institutional repository terms
- Track A suitability: No
- Track B suitability: Conditional, if measured quality and laboratory metadata are explicitly documented

## Candidate 3 — University or public laboratory clinker characterization datasets

- Source: Academic repositories / university open data pages
- DOI/URL: Repository-specific DOI or landing page
- Sample count: Small to moderate, often lab-synthesized or lab-scale
- XRF: Often present
- XRD: Often present
- Rietveld: Possibly present
- Free CaO: Sometimes present
- C3S/C2S/C3A/C4AF: Often present for lab-scale clinker
- Process data: Limited or absent
- Timestamps: Frequently absent
- Sample IDs: Usually sample IDs, not plant-kiln linkage IDs
- Raw material data: Sometimes available, but not always complete
- License: Institutional repository terms vary
- Track A suitability: Usually no
- Track B suitability: Conditional, laboratory-only quality track

## Candidate 4 — Industrial benchmark or process-reporting datasets in public literature

- Source: Industry paper / conference proceedings / public technical report
- DOI/URL: Publication-specific DOI or public report URL
- Sample count: Limited in most cases
- XRF: Often present
- XRD: Sometimes present
- Rietveld: Unclear, depends on study design
- Free CaO: Sometimes available
- C3S/C2S/C3A/C4AF: Sometimes reported
- Process data: Sometimes present but rarely a complete DCS feed-through sequence
- Timestamps: Variable quality
- Sample IDs: Often not structured for relational linkage
- Raw material data: Sometimes available; often not enough to reconstruct the recipe exactly
- License: Report/industry publication terms apply
- Track A suitability: Generally no
- Track B suitability: Conditional

## Summary assessment

Public sources are unlikely to satisfy the full Track A requirement without direct institutional cooperation. The main gap is not chemistry measurement availability; it is the absence of a real production-link traceability chain:

- raw materials
- measured recipe
- kiln run linkage
- clinker sampling
- measured quality
- timestamps and provenance

For a real Track A program, the most credible path remains an anonymized industrial or university collaboration that supplies a relational production dataset.

## Recommended use

- Use public records only for method validation or exploratory benchmark cases.
- Do not treat public datasets as proof of real plant performance.
- Do not claim Track A readiness based on public literature alone.
