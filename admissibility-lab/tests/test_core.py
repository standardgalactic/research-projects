"""
Tests for adm-lab primitives, graph operations, metrics, generator, and archaeology.
Run: python -m tests.test_core
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from adm_core import State, Continuation, Constraint, Trajectory, AdmissibilitySet
from adm_graph import AdmissibilityGraph
from adm_metrics import AdmissibilityMetrics, TrajectoryMetrics, MetricsDelta, repair_efficiency, MetricsSeries
from adm_generator import DenseGenerator, SparseGenerator, compare_generators
from adm_archaeology import TrajectoryResidueRecord, ArchaeologyExperiment


def test_state_identity():
    s1 = State(label="a")
    s2 = State(label="a")
    assert s1 != s2
    s3 = State(id=s1.id, label="a")
    assert s1 == s3
    print("  ✓ state identity")


def test_continuation():
    s1 = State(label="x")
    s2 = State(label="y")
    c = Continuation(s1, s2, weight=1.5)
    assert c.source == s1 and c.target == s2 and c.weight == 1.5
    print("  ✓ continuation")


def test_admissibility_set_empty():
    s = State(label="isolated")
    adm = AdmissibilitySet(s, [], [])
    assert adm.is_sink and adm.size == 0
    print("  ✓ isolated state is sink")


def test_constraint_filters():
    s1, s2, s3 = State(label="a"), State(label="b"), State(label="c")
    c1 = Continuation(s1, s2, weight=2.0)
    c2 = Continuation(s1, s3, weight=0.5)
    heavy = Constraint(predicate=lambda c: c.weight >= 1.0, name="heavy")
    adm = AdmissibilitySet(s1, [c1, c2], [heavy])
    assert adm.size == 1 and c1 in adm.admissible
    print("  ✓ constraint filters")


def test_graph_reachability():
    g = AdmissibilityGraph(label="test")
    s = [State(label=f"s{i}") for i in range(5)]
    for i in range(4):
        g.add_continuation(Continuation(s[i], s[i+1]))
    assert len(g.reachable(s[0])) == 5
    assert len(g.reachable(s[2])) == 3
    print("  ✓ graph reachability")


def test_graph_damage_and_restore():
    g = AdmissibilityGraph()
    s = [State(label=f"s{i}") for i in range(4)]
    for i in range(3):
        g.add_continuation(Continuation(s[i], s[i+1]))
    pre = len(g.reachable(s[0]))
    rec = g.damage_edges({(s[1].id, s[2].id)})
    assert len(g.reachable(s[0])) < pre
    rec.restore()
    assert len(g.reachable(s[0])) == pre
    print("  ✓ damage and restore")


def test_sink_detection():
    g = AdmissibilityGraph()
    s1, s2 = State(label="source"), State(label="sink")
    g.add_continuation(Continuation(s1, s2))
    sink_labels = {s.label for s in g.sinks()}
    assert "sink" in sink_labels and "source" not in sink_labels
    print("  ✓ sink detection")


def test_metrics():
    from experiments.factories import make_random_dag
    g = make_random_dag(n=15, edge_density=0.2, seed=42)
    m = AdmissibilityMetrics.from_graph(g, "test")
    assert m.state_count >= 1
    assert 0.0 <= m.sink_density <= 1.0
    assert m.reachable_volume >= 0
    print("  ✓ graph metrics")


def test_metrics_delta():
    from experiments.factories import make_random_dag
    g = make_random_dag(n=15, edge_density=0.2, seed=42)
    pre = AdmissibilityMetrics.from_graph(g, "pre")
    g.damage_random(fraction=0.3, rng_seed=1)
    post = AdmissibilityMetrics.from_graph(g, "post")
    delta = pre.delta(post)
    assert delta.volume_change <= 0  # damage should not increase volume
    print("  ✓ metrics delta")


def test_trajectory_metrics():
    from experiments.factories import make_random_dag
    g = make_random_dag(n=12, edge_density=0.25, seed=7)
    states = list(g.states)
    traj = g.walk(states[0], max_steps=20)
    tm = TrajectoryMetrics.from_trajectory(traj)
    assert tm.length > 0
    assert tm.trajectory_entropy >= 0
    assert tm.navigability_arc in ("rising", "falling", "stable", "volatile")
    print("  ✓ trajectory metrics")


def test_metrics_series():
    from experiments.factories import make_hub_and_spoke
    g = make_hub_and_spoke(spokes=4, spoke_length=2)
    series = MetricsSeries(label="test_series")
    m1 = series.record(g, "before")
    g.damage_random(fraction=0.4, rng_seed=42)
    m2 = series.record(g, "after")
    assert len(series.snapshots) == 2
    assert m2.reachable_volume <= m1.reachable_volume
    print("  ✓ metrics series")


def test_repair_efficiency():
    from experiments.factories import make_random_dag
    g = make_random_dag(n=12, edge_density=0.2, seed=5)
    pre = AdmissibilityMetrics.from_graph(g, "pre")
    rec = g.damage_random(fraction=0.3, rng_seed=3)
    post_dmg = AdmissibilityMetrics.from_graph(g, "post_dmg")
    rec.restore()
    post_rep = AdmissibilityMetrics.from_graph(g, "post_rep")
    eff = repair_efficiency(post_dmg, post_rep, max(rec.damage_count, 1))
    assert isinstance(eff, float)
    print("  ✓ repair efficiency")


def test_dense_generator():
    gen = DenseGenerator(n=6)
    states = gen.make_states()
    g = gen.build(states)
    # Dense: all forward edges = n*(n-1)/2 = 15
    assert len(list(g.continuations)) == 15
    print("  ✓ dense generator")


def test_sparse_generator():
    dense = DenseGenerator(n=10)
    sparse = SparseGenerator(n=10, density=0.3, seed=1)
    states = dense.make_states()
    g_dense = dense.build(states)
    g_sparse = sparse.build(states)
    assert len(list(g_dense.continuations)) >= len(list(g_sparse.continuations))
    print("  ✓ sparse generator produces fewer continuations than dense")


def test_compare_generators():
    from adm_core import State
    states = [State(label=f"n{i}") for i in range(8)]
    generators = [
        DenseGenerator(n=8, label="dense"),
        SparseGenerator(n=8, density=0.3, seed=42, label="sparse"),
    ]
    results = compare_generators(generators, shared_states=states)
    assert len(results) == 2
    vols = [r["reachable_volume"] for r in results]
    assert vols[0] >= vols[1]  # dense should have >= volume
    print("  ✓ compare generators: dense ≥ sparse reachable volume")


def test_trajectory_residue():
    from experiments.factories import make_random_dag
    g = make_random_dag(n=12, edge_density=0.25, seed=42)
    residue = TrajectoryResidueRecord()
    states = list(g.states)
    for s in states[:3]:
        traj = g.walk(s, max_steps=15)
        residue.ingest(traj)
    assert residue.trajectory_count == 3
    assert len(residue.state_visits) > 0
    print("  ✓ trajectory residue record")


def test_archaeology_experiment():
    from experiments.factories import make_hub_and_spoke
    g = make_hub_and_spoke(spokes=4, spoke_length=2)
    exp = ArchaeologyExperiment(graph=g, seed=99)
    curve = exp.run(max_trajectories=40, measure_every=10, verbose=False)
    assert len(curve) > 0
    assert all(0.0 <= f.overall_fidelity <= 1.0 for f in curve)
    print("  ✓ archaeology experiment")


def run_all():
    print("\n" + "="*60)
    print("ADM-LAB TEST SUITE")
    print("="*60)
    tests = [
        test_state_identity,
        test_continuation,
        test_admissibility_set_empty,
        test_constraint_filters,
        test_graph_reachability,
        test_graph_damage_and_restore,
        test_sink_detection,
        test_metrics,
        test_metrics_delta,
        test_trajectory_metrics,
        test_metrics_series,
        test_repair_efficiency,
        test_dense_generator,
        test_sparse_generator,
        test_compare_generators,
        test_trajectory_residue,
        test_archaeology_experiment,
    ]
    passed = failed = 0
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"  ✗ {test.__name__}: {e}")
            import traceback; traceback.print_exc()
            failed += 1
    print(f"\n{passed} passed, {failed} failed")
    print("="*60)
    return failed == 0


if __name__ == "__main__":
    success = run_all()
    sys.exit(0 if success else 1)
