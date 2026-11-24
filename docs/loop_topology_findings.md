# Loop topology findings (toy models)

Status: results from standard-library Markov toy models, not lab data.
Co-authored (JinnZ2 + Claude), 2026-11-23. Filed here 2026-11-24 from the
work order that states them. The toy-model code is not in this repository
and none of the results below was rerun when this file was written.

Tags used in this file: REPORTED (a toy-model result as stated in the work
order, not rerun here), PROPOSED (a rule or instrument not yet tested),
OBSERVED (seen in this repository, with the command that shows it).

## Scope

- Small driven Markov models built with the standard library only.
- No organism, colony or instrument was measured.
- No number is given here: none was delivered with the findings.

## Findings

1. **Weld: net flow is read, total flow is paid for.** REPORTED.
   A cut reads net flow across it. Cost scales with total flow. Two opposing
   flows in one bin read 0 while both are paid for. Instances named: Joule
   heating (I squared R), kinetic energy (one half m v squared), a futile
   cycle (current times affinity), migration. The gap between the two
   readings is a convexity (Jensen) gap.

2. **Static mutual information can be 0 across a cut that all dissipation
   crosses.** REPORTED. Model: a driven two-unit loop. Static mutual
   information is the wrong instrument for placing a cut.

3. **Transfer entropy sees coupling, not direction of the loop.** REPORTED.
   It is symmetric in the model, so it shows that the units are coupled and
   not which way the loop turns. It fades as the sampling interval grows
   past the loop period.

4. **Schnakenberg decomposition.** REPORTED. Entropy production equals loop
   current times loop affinity. The cost lives in closed loops of the rate
   graph, not in states.

5. **Dwell-time plus entry/exit observation.** REPORTED. The loop cost is
   recovered in full if a loop is still visible after the cut. It reads 0 if
   the cut collapses the loop into a tree, at any drive strength.

6. **Nested fast and slow loops.** REPORTED.
   - Spatial cuts remove loops whole, and the removed costs add.
   - Lumping a loop's own tightly coupled states into one state erases that
     loop (adiabatic elimination).
   - Time cuts (slower sampling) remove the fastest loop first.

## Proposed

- **Rule.** PROPOSED. A loop's cost stays visible only if the cut keeps at
  least 3 of its states distinguishable in cyclic order and samples faster
  than the loop period.
- **Instrument.** PROPOSED. Calorimeter heat (which does not depend on the
  cut) minus the information-ledger reading equals the hidden loop cost.

## Instance in this repository

OBSERVED. `scripts/build_index.py` read links in one shape only
(`relation` / `target`). Records under `ontology/social/` write links as
`rel` / `to`, so every link from a social record read as 0 in
`ontology_index.json`. Reading both shapes moved the relation count from
541 to 553 with the same 120 entities (`python3 scripts/build_index.py`,
2026-11-24). The 12 added relations were in the files the whole time; the
reader's cut left them out.

## Where this is used

`docs/coordination_layer.md`: the `loop_topology.observer_cuts` field of a
coordination block lists, for each way of observing, which cycles are still
inside the record.

## Provenance

Findings 1 to 6 and the two proposals: stated in the work order of
2026-11-24 (Kavik + Claude), dated 2026-11-23 there. The repository
instance: run in this repository on branch `coordination-layer`.
