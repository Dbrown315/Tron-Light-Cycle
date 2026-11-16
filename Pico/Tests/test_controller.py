"""Exercise MicroPython button polling and packet output with fake hardware."""
import importlib.util
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

CONTROLLER = Path(__file__).resolve().parents[1] / 'controller'


def load(name):
    spec = importlib.util.spec_from_file_location('test_pico_' + name,
                                                 CONTROLLER / (name + '.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class PicoControllerTests(unittest.TestCase):
    def setUp(self):
        self.settings = load('config').DEFAULTS

    def test_a_b_gpio_debounce_hold_and_repress(self):
        now = [0]
        pins = {}

        class Pin:
            IN = 0
            PULL_UP = 1

            def __init__(self, gpio, mode, pull):
                self.raw = 1
                self.mode, self.pull = mode, pull
                pins[gpio] = self

            def value(self):
                return self.raw

        clock = SimpleNamespace(ticks_ms=lambda: now[0],
                                ticks_diff=lambda a, b: a - b)
        with patch.dict('sys.modules', machine=SimpleNamespace(Pin=Pin),
                        config=SimpleNamespace(SETTINGS=self.settings), time=clock):
            buttons = load('buttons')
        for button, gpio in (('A', 22), ('B', 21)):
            with self.subTest(button=button):
                self.assertIs(buttons.BUTTONS[button], pins[gpio])
                self.assertEqual(pins[gpio].pull, Pin.PULL_UP)
                pins[gpio].raw = 0
                self.assertIsNone(buttons.get_button_press())
                now[0] += 10
                pins[gpio].raw = 1  # Bounce resets the debounce timer.
                self.assertIsNone(buttons.get_button_press())
                pins[gpio].raw = 0
                self.assertIsNone(buttons.get_button_press())
                now[0] += 19
                self.assertIsNone(buttons.get_button_press())
                now[0] += 1
                self.assertEqual(buttons.get_button_press(), button)
                now[0] += 100
                self.assertIsNone(buttons.get_button_press())
                pins[gpio].raw = 1
                buttons.get_button_press()
                now[0] += 20
                self.assertIsNone(buttons.get_button_press())
                pins[gpio].raw = 0
                buttons.get_button_press()
                now[0] += 20
                self.assertEqual(buttons.get_button_press(), button)
                pins[gpio].raw = 1
                buttons.get_button_press()
                now[0] += 20
                buttons.get_button_press()

    def test_six_button_packets_and_direction_compatibility(self):
        ble = Mock()
        ble.gatts_register_services.return_value = ((42,),)
        bluetooth = SimpleNamespace(BLE=lambda: ble, UUID=lambda value: value)
        clock = SimpleNamespace(ticks_ms=lambda: 0x04030201)
        with patch.dict('sys.modules', bluetooth=bluetooth,
                        micropython=SimpleNamespace(const=lambda value: value),
                        config=SimpleNamespace(SETTINGS=self.settings), time=clock):
            sender = load('ble_controller')
        sender.connections.add(7)
        for code, button in enumerate(('UP', 'DOWN', 'LEFT', 'RIGHT', 'A', 'B'), 1):
            sender.send_button(button)
            packet = bytes((code, 1, 2, 3, 4))
            ble.gatts_write.assert_called_with(42, packet)
            ble.gatts_notify.assert_called_with(7, 42, packet)
        sender.send_direction('UP')
        ble.gatts_notify.assert_called_with(7, 42, b'\x01\x01\x02\x03\x04')
        count = ble.gatts_notify.call_count
        sender.send_button('UNKNOWN')
        self.assertEqual(ble.gatts_notify.call_count, count)
