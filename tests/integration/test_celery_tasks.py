def test_scan_member_task_has_delay():
    from app.tasks.detection_tasks import scan_member

    assert hasattr(scan_member, "delay")
