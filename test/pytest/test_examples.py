# ArseneWenger
# April 2022
# Test the help function

def test_ping():
    """
    :return boolean
    """
    assert get_ping() == "pong", "ping did not return pong"