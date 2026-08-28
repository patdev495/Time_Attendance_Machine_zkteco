import pytest
from datetime import datetime, date
from backend.src.database import AttendanceLog, EmployeeLocalRegistry, EmployeeMetadata

def seed_logs_data(db_session):
    # Setup Employees in Registry
    emp1 = EmployeeLocalRegistry(employee_id="EMP001", emp_name="Nguyen Van A", department="Office")
    emp2 = EmployeeLocalRegistry(employee_id="EMP002", emp_name="Tran Thi B", department="Workshop")
    db_session.add_all([emp1, emp2])
    db_session.commit()

    # Create 105 attendance logs
    logs = []
    for i in range(1, 106):
        emp_id = "EMP001" if i % 2 == 1 else "EMP002"
        day = (i % 28) + 1
        hour = 8 if i % 2 == 1 else 17
        log_dt = datetime(2026, 4, day, hour, i % 60, 0)
        logs.append(AttendanceLog(
            employee_id=emp_id,
            attendance_date=date(2026, 4, day),
            attendance_time=log_dt,
            machine_ip="192.168.1.201" if i % 3 != 0 else "192.168.1.202"
        ))
    db_session.add_all(logs)
    db_session.commit()

def test_get_logs_pagination_and_count(client, db_session):
    seed_logs_data(db_session)

    response = client.get("/api/logs?page=1&size=50")
    assert response.status_code == 200
    data = response.json()

    assert data["total_count"] == 105
    assert data["total_pages"] == 3
    assert len(data["items"]) == 50

    # Ensure items are ordered by attendance_time desc
    times = [item["attendance_time"] for item in data["items"]]
    assert times == sorted(times, reverse=True)

    # Page 2
    response_p2 = client.get("/api/logs?page=2&size=50")
    assert response_p2.status_code == 200
    data_p2 = response_p2.json()
    assert len(data_p2["items"]) == 50

    # Page 3
    response_p3 = client.get("/api/logs?page=3&size=50")
    assert response_p3.status_code == 200
    data_p3 = response_p3.json()
    assert len(data_p3["items"]) == 5

def test_get_logs_date_range_filter(client, db_session):
    seed_logs_data(db_session)

    # Filter for date range 2026-04-01 to 2026-04-05
    response = client.get("/api/logs?start_date=2026-04-01&end_date=2026-04-05")
    assert response.status_code == 200
    data = response.json()
    
    assert data["total_count"] > 0
    for item in data["items"]:
        log_date = item["attendance_time"][:10]
        assert "2026-04-01" <= log_date <= "2026-04-05"

def test_get_logs_employee_id_filter(client, db_session):
    seed_logs_data(db_session)

    # Search by exact ID
    res = client.get("/api/logs?employee_id=EMP001")
    assert res.status_code == 200
    data = res.json()
    assert data["total_count"] == 53 # odd numbers 1..105 -> 53 items
    for item in data["items"]:
        assert item["employee_id"] == "EMP001"
        assert item["emp_name"] == "Nguyen Van A"

    # Search by name substring
    res_name = client.get("/api/logs?employee_id=Tran")
    assert res_name.status_code == 200
    data_name = res_name.json()
    assert data_name["total_count"] == 52 # even numbers 2..104 -> 52 items
    for item in data_name["items"]:
        assert item["employee_id"] == "EMP002"
        assert item["emp_name"] == "Tran Thi B"

def test_get_logs_machine_ip_filter(client, db_session):
    seed_logs_data(db_session)

    res = client.get("/api/logs?machine_ip=192.168.1.202")
    assert res.status_code == 200
    data = res.json()
    assert data["total_count"] == 35 # 105 // 3 = 35
    for item in data["items"]:
        assert item["machine_ip"] == "192.168.1.202"

def test_get_logs_employee_metadata_fallback_and_missing(client, db_session):
    # Setup emp with metadata only, and emp with no registry entry
    db_session.add(EmployeeMetadata(employee_id="META01", emp_name="Le Van Meta"))
    db_session.add_all([
        AttendanceLog(
            employee_id="META01",
            attendance_date=date(2026, 4, 10),
            attendance_time=datetime(2026, 4, 10, 8, 0, 0),
            machine_ip="192.168.1.201"
        ),
        AttendanceLog(
            employee_id="UNKNOWN99",
            attendance_date=date(2026, 4, 10),
            attendance_time=datetime(2026, 4, 10, 8, 5, 0),
            machine_ip="192.168.1.201"
        )
    ])
    db_session.commit()

    res = client.get("/api/logs?employee_id=META01")
    assert res.status_code == 200
    data = res.json()
    assert data["total_count"] == 1
    assert data["items"][0]["emp_name"] == "Le Van Meta"

    res_unk = client.get("/api/logs?employee_id=UNKNOWN99")
    assert res_unk.status_code == 200
    data_unk = res_unk.json()
    assert data_unk["total_count"] == 1
    assert data_unk["items"][0]["emp_name"] is None
