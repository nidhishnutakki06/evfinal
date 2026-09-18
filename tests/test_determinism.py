from sh305.synthetic.generator import SyntheticDataGenerator


def test_deterministic_generation_reproducibility():
    """
    Verify that running the generator twice with the exact same seed produces
    strictly identical values across all generated entities and SystemState.
    """
    gen1 = SyntheticDataGenerator(seed=12345)
    state1 = gen1.generate_initial_system_state(ev_count=8, station_count=8)

    gen2 = SyntheticDataGenerator(seed=12345)
    state2 = gen2.generate_initial_system_state(ev_count=8, station_count=8)

    # Validate exact equality of models and serialized dictionary representations
    assert state1 == state2
    assert state1.model_dump() == state2.model_dump()


def test_generator_reset_reproducibility():
    """
    Verify that calling reset() on an existing generator returns it to the
    exact starting sequence.
    """
    gen = SyntheticDataGenerator(seed=999)
    evs_run1 = gen.generate_evs(count=8)

    gen.reset(seed=999)
    evs_run2 = gen.generate_evs(count=8)

    assert evs_run1 == evs_run2
    for ev1, ev2 in zip(evs_run1, evs_run2):
        assert ev1.model_dump() == ev2.model_dump()


def test_different_seeds_produce_different_data():
    """Verify that different seeds produce distinct synthetic profiles."""
    gen_a = SyntheticDataGenerator(seed=42)
    evs_a = gen_a.generate_evs(count=8)

    gen_b = SyntheticDataGenerator(seed=100)
    evs_b = gen_b.generate_evs(count=8)

    assert evs_a != evs_b
    assert [e.current_soc for e in evs_a] != [e.current_soc for e in evs_b]
