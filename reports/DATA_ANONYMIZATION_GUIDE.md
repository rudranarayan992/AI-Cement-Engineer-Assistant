# DATA ANONYMIZATION GUIDE

This guide explains how industrial data can be shared without revealing confidential commercial information while preserving scientific validity.

## Core principle

The data must preserve relationships between records while removing direct identifiers.

Example:

- Company name: withheld
- Plant name: `Plant_A`
- Kiln ID: `Kiln_1`
- Sample ID: `Sample_0001`
- Raw mix ID: `RM_001`
- Kiln run ID: `RUN_001`

This replaces business-sensitive labels with coded identifiers while maintaining the real scientific links:

- raw material -> raw mix -> kiln run -> clinker sample

## What may be anonymized

Acceptable anonymization includes:

- plant code instead of plant name
- kiln code instead of kiln serial number
- sample code instead of customer or production batch labels
- generic raw-material categories instead of proprietary material names
- coded process record IDs instead of operational labels

## What should not be required

The following should not be required unless scientifically necessary:

- company name
- exact geographic location
- proprietary recipe names
- exact operating limits
- confidential market or production strategy details

These are not needed to validate the process-to-clinker relationship.

## What must be preserved

The following must remain intact:

- Plant_ID
- Kiln_ID
- Raw_Mix_ID
- Kiln_Run_ID
- Sample_ID
- Production_DateTime
- Sampling_DateTime
- Measurement_DateTime
- measurement method
- units and basis
- provenance metadata

## Recommended anonymization pattern

Use a simple coded scheme such as:

- Plant_A, Plant_B, Plant_C
- Kiln_1, Kiln_2, Kiln_3
- Sample_0001, Sample_0002
- RM_001, RM_002
- RUN_001, RUN_002

This keeps the dataset scientifically traceable while anonymizing the underlying plant identity.

## Relationship preservation

The anonymized IDs must map consistently across tables:

- raw material table: `Material_ID` and `Plant_ID`
- raw mix table: `Raw_Mix_ID` and `Plant_ID`
- kiln process table: `Kiln_Run_ID`, `Plant_ID`, `Kiln_ID`
- clinker table: `Sample_ID`, `Raw_Mix_ID`, `Kiln_Run_ID`, `Plant_ID`, `Kiln_ID`

## Acceptable release standard

A dataset should be considered acceptable for anonymized sharing when:

- direct identifiers are removed or coded
- sample-to-process relationships remain valid
- timestamps and operating windows remain intact
- measurement methods remain explicit
- provenance remains documented

This allows a plant or lab to contribute real, scientifically useful data without exposing commercially sensitive information.
