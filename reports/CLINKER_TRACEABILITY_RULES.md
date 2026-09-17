# CLINKER TRACEABILITY RULES

## Required chain

A valid industrial clinker dataset must support the production chain:

raw material -> raw mix -> kiln run -> clinker sample

This relationship must be established by documented identifiers or a defensible production window, not by nearest-timestamp matching alone.

## Required linkage fields

Each clinker sample must be linked to:

- Sample_ID linkage
- Raw_Mix_ID linkage
- Kiln_Run_ID linkage
- Plant_ID
- Kiln_ID
- production timestamp
- sampling timestamp
- residence time or production-window estimate
- sampling delay
- production window or process window

## Why nearest timestamps are not sufficient

Nearest-timestamp matching alone is not scientifically sufficient because:

1. Raw material chemistry may vary by stockpile, silo, and shipment timing.
2. Raw-mix composition changes over time and may be blended before feeding the kiln.
3. Kiln residence time, feed rate, and thermal profile cause lag between process conditions and clinker sampling.
4. Sampling delay and cooler handling can decouple the pyroprocessing conditions from the final measured clinker.
5. Different plants and kilns can operate with materially different residence times and feed patterns even when timestamps look similar.
6. A coincidence in date-time proximity is not proof of production linkage.

A valid dataset must therefore provide documented chain-of-custody identifiers, production windows, and actual process linkage beyond time proximity.

## Scientific acceptance standard

A dataset may be considered traceable only if at least one of the following is documented:

- an explicit `Raw_Mix_ID` linked to a clinker sample
- an explicit `Kiln_Run_ID` linked to a clinker sample
- a valid production window supported by process records and sampling time
- a documented kiln residence-time or delay estimate that justifies the temporal relationship

If none of the above is present, the data must be treated as non-traceable.

## Minimum traceability check

A sample should be rejected for the main industrial track when:

- no sample ID is present
- no plant/kiln IDs are present
- no raw-mix or kiln-run linkage exists
- timestamps are missing or invalid
- the date-time relationship cannot be defended scientifically
- the dataset relies only on nearest-neighbor matching without production-window justification

## Data provenance expectation

The dataset should include provenance for:

- raw-material source
- raw-mix record
- kiln process records
- clinker measurement lab
- measurement date and method
- instrument and replicate information

Without these links, the project cannot legitimately claim industrial clinker traceability.
