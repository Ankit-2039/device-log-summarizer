import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from device_log_summarizer import clean_sensor_readings


def test_mixed_input():
    data = [10, "25.5", None, "abc", -3, 700, "450"]
    assert clean_sensor_readings(data) == [10.0, 25.5, 500.0, 450.0]


def test_empty_list():
    assert clean_sensor_readings([]) == []


def test_all_invalid():
    assert clean_sensor_readings([None, "bad", -1, "-5", float("nan")]) == []


if __name__ == "__main__":
    test_mixed_input()
    test_empty_list()
    test_all_invalid()
    print("All tests passed.")