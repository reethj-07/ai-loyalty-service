from app.ml.rfm_engine import RFMEngine



def test_segment_boundary_conditions():
    engine = RFMEngine()

    assert engine.assign_named_segment(4.0) == "Champions"
    assert engine.assign_named_segment(3.1) == "Loyal"
    assert engine.assign_named_segment(2.3) == "At Risk"
    assert engine.assign_named_segment(1.4) == "Dormant"
    assert engine.assign_named_segment(0.8) == "New"
