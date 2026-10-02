# Extractor validation: v1

64 hand-labelled responses (stratified, `validation/sample.jsonl`), compared with `extractions.jsonl` after the run's taxonomy is applied to both sides.

- response_type agreement: 57/64 (89%)
- subject_sense agreement: 63/64 (98%)
- concepts (on-subject, same-language responses): precision 0.82, recall 0.69, F1 0.75 (tp 480, fp 104, fn 216)
- tradition agreement on shared concepts: 453/480 (94%)
- per-response net valence, extractor minus labels: mean +0.00, mean absolute 0.07 (n=57)

## Net valence by language (mean over responses, concept presence)

| lang | labels | extractor | n |
|---|---|---|---|
| en | +0.01 | -0.02 | 15 |
| ja | +0.19 | +0.15 | 16 |
| ko | +0.22 | +0.31 | 12 |
| zh | +0.27 | +0.25 | 15 |

## response_type confusion (label → extractor)

| label \ extractor | definition | completion | clarification | multi_sense | refusal | other |
|---|---|---|---|---|---|---|
| definition | 34 |  | 1 | 2 |  |  |
| completion |  |  |  | 2 |  |  |
| clarification |  |  | 8 | 2 |  |  |
| multi_sense |  |  |  | 14 |  |  |
| other |  |  |  |  |  | 1 |

## subject_sense (label, extractor): False/False 2, False/True 1, True/True 61

## Concepts the extractor missed most

mythical creature (14), clouds (11), folklore (10), large (9), water (8), composite (8), sacred (7), scales (6), wings (6), weather control (6), zodiac (6), important (6), rain (6), claws (6), reptilian (5), slain (5), horns (5), water control (5), hoarding (4), divine (4), head (4), media (3), water deity (3), royalty (3), serpentine (3)

## Concepts only the extractor found

creature (9), control (6), symbol (5), weather (5), divine (4), mythical creature (4), fish (4), serpentine (4), eagle (4), water (4), mythology (3), deer (3), flight (2), guardian (2), body (2), fierce (2), resilience (2), folklore (2), culture (2), cosmos (1), disaster (1), people (1), head (1), constellation (1), chinese (1)
