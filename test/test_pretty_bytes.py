from codebasegpt import pretty_bytes as pb


def test_pretty_bytes_for_bytes():
    assert pb.bytes_to_str(100) == '100 B'
    assert pb.bytes_to_str(999) == '999 B'


def test_pretty_bytes_for_kilobytes():
    assert pb.bytes_to_str(1000) == '1.0 KB'
    assert pb.bytes_to_str(1500) == '1.5 KB'


def test_pretty_bytes_for_megabytes():
    assert pb.bytes_to_str(1000**2) == '1.0 MB'
    assert pb.bytes_to_str(5 * 1000**2) == '5.0 MB'


def test_pretty_bytes_for_gigabytes():
    assert pb.bytes_to_str(1000**3) == '1.0 GB'
    assert pb.bytes_to_str(3.5 * 1000**3) == '3.5 GB'


def test_pretty_bytes_for_terabytes_and_beyond():
    assert pb.bytes_to_str(1000**4) == '1.0 TB'
    assert pb.bytes_to_str(1000**5) == '1.0 PB'
    assert pb.bytes_to_str(1000**6) == '1.0 EB'
    assert pb.bytes_to_str(1000**7) == '1.0 ZB'
    assert pb.bytes_to_str(1000**8) == '1.0 YB'

