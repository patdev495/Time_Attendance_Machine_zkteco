import pytest
from datetime import datetime, date, time
from backend.src.utils.stats_utils import compute_day_stats
from backend.src.database import ShiftDefinition

def setup_standard_rules(db_session):
    # Default Day
    db_session.add(ShiftDefinition(
        shift_code="N",
        start_time=time(8, 0), end_time=time(17, 0),
        is_night_shift=False, work_hours=8.0, standard_hours=8.0,
        break_hours=1.0, workday_base=8.0
    ))
    # Default Night
    db_session.add(ShiftDefinition(
        shift_code="D",
        start_time=time(20, 0), end_time=time(5, 0),
        is_night_shift=True, work_hours=8.0, standard_hours=8.0,
        break_hours=1.0, workday_base=8.0
    ))
    # Xuong 1 12h Day
    db_session.add(ShiftDefinition(
        shift_code="12N",
        start_time=time(8, 0), end_time=time(20, 0),
        is_night_shift=False, work_hours=12.0, standard_hours=12.0,
        break_hours=0.0, workday_base=8.0
    ))
    db_session.commit()
    return db_session.query(ShiftDefinition).all()

def test_compute_day_stats_standard_day(db_session):
    rules_pool = setup_standard_rules(db_session)
    
    # 08:30 -> 17:30 (Late 30m, No Early, 8h Standard, 0.0h OT)
    first = datetime(2026, 4, 7, 8, 30)
    last = datetime(2026, 4, 7, 17, 30)
    d = date(2026, 4, 7)
    
    # department="Office", shift="N"
    _, hours_std, hours_ot, min_late, min_early = compute_day_stats(first, last, d, "Office", "N", rules_pool=rules_pool)[:5]
    
    assert min_late == 30
    assert min_early == 0
    assert hours_std == 8.0
    assert hours_ot == 0.0

def test_compute_day_stats_standard_night(db_session):
    rules_pool = setup_standard_rules(db_session)
    
    # 20:05 -> 06:35 (Late 5m, No Early, 8h Standard, 1.5h OT since 1h35m OT rounds down to 1.5h)
    first = datetime(2026, 4, 7, 20, 5)
    last = datetime(2026, 4, 8, 6, 35)
    d = date(2026, 4, 7)
    
    _, hours_std, hours_ot, min_late, min_early = compute_day_stats(first, last, d, "Store", "D", rules_pool=rules_pool)[:5]
    
    assert min_late == 5
    assert min_early == 0
    assert hours_std == 8.0
    assert hours_ot == 1.5

def test_compute_day_stats_early_leave(db_session):
    rules_pool = setup_standard_rules(db_session)
    
    # 07:55 -> 16:50 (No Late, Early 10m, 7.83...h Standard)
    # Total duration: 8h 55m. Deduct 1h break = 7h 55m = 7.91... hours
    first = datetime(2026, 4, 7, 7, 55)
    last = datetime(2026, 4, 7, 16, 50)
    d = date(2026, 4, 7)
    
    _, hours_std, hours_ot, min_late, min_early = compute_day_stats(first, last, d, "Office", "N", rules_pool=rules_pool)[:5]
    
    assert min_late == 0
    assert min_early == 10
    # 16:50 - 08:00 = 8h 50m. Deduct 1h = 7h 50m = 7.833...
    assert round(hours_std, 2) == 7.83

def test_compute_day_stats_xuong1_day(db_session):
    rules_pool = setup_standard_rules(db_session)
    
    # 12N: 08:00-20:00, 12h std, no break, no OT
    # 07:50 -> 20:10
    first = datetime(2026, 4, 7, 7, 50)
    last = datetime(2026, 4, 7, 20, 10)
    d = date(2026, 4, 7)
    
    _, hours_std, hours_ot, min_late, min_early = compute_day_stats(first, last, d, "Xưởng 1 - Phụ kiện", "12N", rules_pool=rules_pool)[:5]
    
    assert min_late == 0
    assert min_early == 0
    assert hours_std == 12.0
    assert hours_ot == 0.0

def test_compute_day_stats_missing_last_tap(db_session):
    rules_pool = setup_standard_rules(db_session)
    
    first = datetime(2026, 4, 7, 8, 0)
    last = first # Only one tap
    d = date(2026, 4, 7)
    
    _, hours_std, hours_ot, min_late, min_early = compute_day_stats(first, last, d, "Office", "N", rules_pool=rules_pool)[:5]
    
    assert hours_std == 0
    assert hours_ot == 0

