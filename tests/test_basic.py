from decimal import Decimal
import os
import sys

# shunt '..' into sys.path since we are in a 'tests' subdirectory
base_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
if base_dir not in sys.path:
    sys.path.insert(0, base_dir)

from nsq import BackoffTimer
import nsq


def pytest_generate_tests(metafunc):
    if metafunc.function == test_topic_names:
        for name, good in [
                ('valid_name', True),
                ('invalid name with space', False),
                ('invalid_name_due_to_length_this_is_really_long', False),
                ('test-with_period.', True),
                ('test#ephemeral', False),
                ('test:ephemeral', False),
            ]:
            metafunc.addcall(funcargs=dict(name=name, good=good))
    if metafunc.function == test_channel_names:
        for name, good in [
                ('test', True),
                ('test-with_period.', True),
                ('test#ephemeral', True),
                ('invalid_name_due_to_length_this_is_really_long', False),
                ('invalid name with space', False),
            ]:
            metafunc.addcall(funcargs=dict(name=name, good=good))

def test_topic_names(name, good):
    assert nsq.valid_topic_name(name) == good

def test_channel_names(name, good):
    assert nsq.valid_channel_name(name) == good

def test_backoff_timer():
    timer = BackoffTimer(.1, 120, long_length=1000)
    assert timer.get_interval() == .1
    timer.success()
    assert timer.get_interval() == .1
    timer.failure()
    interval = '%0.2f' % timer.get_interval()
    assert interval == '3.19'
    assert timer.min_interval == Decimal('.1')
    assert timer.short_interval == Decimal('2.9975')
    assert timer.long_interval == Decimal('0.089925')
    
    timer.failure()
    interval = '%0.2f' % timer.get_interval()
    assert interval == '6.27'
    timer.success()
    interval = '%0.2f' % timer.get_interval()
    assert interval == '3.19'
    for i in range(25):
        timer.failure()
    interval = '%0.2f' % timer.get_interval()
    assert interval == '32.41'