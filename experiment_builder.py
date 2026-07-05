def build_experiments_from_ontology(json_path: str) -> list[Experiment]:
    with open(json_path) as f:
        onto = json.load(f)
    entities = {e["id"]: e for e in onto["entities"]}
    experiments = []

    for rel in onto["relations"]:
        src_id = rel["source"]
        tgt_id = rel["target"]
        rel_type = rel["relation"]

        src = entities[src_id]
        tgt = entities[tgt_id]

        if rel_type == "synergy":
            # Run both topologies under same dynamics and compare
            topo_src = get_component(src, "topology")
            topo_tgt = get_component(tgt, "topology")
            dyn = get_component(src, "dynamics") or get_component(tgt, "dynamics") or ThermalDiffusion()
            metric = get_component(src, "metric") or get_component(tgt, "metric") or SignalIntegrity()
            fail = get_component(src, "failure") or get_component(tgt, "failure") or PhaseTransition(threshold=0.4)

            exp_src = Experiment(
                topology=topo_src,
                dynamics=dyn,
                perturbations=[],
                metrics={"primary": metric},
                failure_model=fail,
                total_time=100.0
            )
            exp_tgt = Experiment(
                topology=topo_tgt,
                dynamics=dyn,
                perturbations=[],
                metrics={"primary": metric},
                failure_model=fail,
                total_time=100.0
            )
            experiments.extend([exp_src, exp_tgt])

        elif rel_type == "energy_coupling":
            # Source acts as perturbation on target
            topo = get_component(tgt, "topology")
            pert = get_component(src, "perturbation") or LocalizedHeat(node=0, energy=50, time=1.0)
            dyn = get_component(tgt, "dynamics") or ThermalDiffusion()
            metric = get_component(tgt, "metric") or SignalIntegrity()
            fail = get_component(tgt, "failure") or PhaseTransition(threshold=0.4)

            exp = Experiment(
                topology=topo,
                dynamics=dyn,
                perturbations=[pert],
                metrics={"primary": metric},
                failure_model=fail,
                total_time=100.0
            )
            experiments.append(exp)

        elif rel_type == "temporal_bridge":
            # Compare failure trajectories
            fail_src = get_component(src, "failure") or HysteresisFailure()
            fail_tgt = get_component(tgt, "failure") or HysteresisFailure()
            topo = get_component(src, "topology") or GridTopology(10,10)
            dyn = get_component(src, "dynamics") or ThermalDiffusion()
            metric = get_component(src, "metric") or SignalIntegrity()

            exp_src = Experiment(
                topology=topo, dynamics=dyn, perturbations=[],
                metrics={"primary": metric}, failure_model=fail_src,
                total_time=100.0
            )
            exp_tgt = Experiment(
                topology=topo, dynamics=dyn, perturbations=[],
                metrics={"primary": metric}, failure_model=fail_tgt,
                total_time=100.0
            )
            experiments.extend([exp_src, exp_tgt])

        elif rel_type == "resonance":
            # Measure coherence metric between them
            topo = get_component(src, "topology") or GridTopology(10,10)
            dyn = get_component(src, "dynamics") or ThermalDiffusion()
            metric = Coherence()  # resonance → coherence
            fail = get_component(src, "failure") or PhaseTransition(threshold=0.2)

            exp = Experiment(
                topology=topo, dynamics=dyn, perturbations=[],
                metrics={"coherence": metric}, failure_model=fail,
                total_time=100.0
            )
            experiments.append(exp)

        elif rel_type == "geometry_link":
            # Source provides topology for target
            pass  # handled by topology registry already

    return experiments

