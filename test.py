from rich.table import Table
from main import disk_info_cal
from main import net_info_cal
from main import cpu_table_1
from main import cpu_table_2
from main import ram_table
from main import disk_table_1
from main import disk_table_2
from main import network_table
from main import bat_table
from main import fan_table
from main import process_table_1
from main import process_table_2


def test_disk_info_cal():
    results = disk_info_cal()
    for result in results:
        assert hasattr(result, "drive")
        assert hasattr(result, "read")
        assert hasattr(result, "write")
        assert hasattr(result, "count_r")
        assert hasattr(result, "count_w")

        assert isinstance(result.drive, str)
        assert isinstance(result.read, float)
        assert isinstance(result.write, float)
        assert isinstance(result.count_r, int)
        assert isinstance(result.count_w, int)


def test_net_info_cal():
    results = net_info_cal()
    for result in results:
        assert hasattr(result, "device")
        assert hasattr(result, "upload")
        assert hasattr(result, "download")
        assert hasattr(result, "sent")
        assert hasattr(result, "recv")

        assert isinstance(result.device, str)
        assert isinstance(result.upload, float)
        assert isinstance(result.download, float)
        assert isinstance(result.sent, float)
        assert isinstance(result.recv, float)


def test_cpu_table_1():
    table = cpu_table_1()
    assert isinstance(table, Table)
    assert len(table.columns) == 3


def test_cpu_table_2():
    table = cpu_table_2()
    assert isinstance(table, Table)
    assert len(table.columns) == 2
    assert len(table.rows) == 2


def test_ram_table():
    table = ram_table()
    assert isinstance(table, Table)
    assert len(table.columns) == 5
    assert len(table.rows) == 3


def test_disk_table_1():
    table = disk_table_1()
    assert isinstance(table, Table)
    assert len(table.columns) == 5


def test_disk_table_2():
    table = disk_table_2()
    assert isinstance(table, Table)
    assert len(table.columns) == 3


def test_network_table():
    table = network_table()
    assert isinstance(table, Table)
    assert len(table.columns) == 5


def test_bat_table():
    table = bat_table()
    assert isinstance(table, Table)
    assert len(table.columns) == 1
    assert len(table.rows) == 2


def test_fan_table():
    table = fan_table()
    assert isinstance(table, Table)
    assert len(table.columns) == 3


def test_process_table_1():
    table = process_table_1()
    assert isinstance(table, Table)
    assert len(table.columns) == 8


def test_process_table_2():
    table = process_table_2(0, 50)
    assert isinstance(table, Table)
    assert len(table.columns) == 8
