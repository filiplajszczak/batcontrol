from unittest.mock import call

import pytest

from batcontrol.inverter.dummy import Dummy
from batcontrol.inverter.mqtt_inverter import MqttInverter


@pytest.fixture
def dummy_inverter():
    return Dummy({'max_grid_charge_rate': 5000})


@pytest.fixture
def activated_mqtt_inverter(mocker):
    inverter = MqttInverter(
        {
            'base_topic': 'inverter',
            'capacity': 10000,
            'max_grid_charge_rate': 5000,
        }
    )
    mock_mqtt_api = mocker.MagicMock()
    mock_client = mocker.MagicMock()
    mock_mqtt_api.client = mock_client
    inverter.activate_mqtt(mock_mqtt_api)
    return inverter, mock_client


def test_dummy_force_charge_sets_force_charge_mode(dummy_inverter):
    inverter = dummy_inverter

    inverter.set_mode_force_charge(3000)

    assert inverter.mode == 'force_charge'


def test_dummy_avoid_discharge_sets_avoid_discharge_mode(dummy_inverter):
    inverter = dummy_inverter

    inverter.set_mode_avoid_discharge()

    assert inverter.mode == 'avoid_discharge'


def test_dummy_allow_discharge_sets_allow_discharge_mode(dummy_inverter):
    inverter = dummy_inverter

    inverter.set_mode_allow_discharge()

    assert inverter.mode == 'allow_discharge'


def test_dummy_limit_battery_charge_sets_limit_battery_charge_mode(dummy_inverter):
    inverter = dummy_inverter

    inverter.set_mode_limit_battery_charge(2000)

    assert inverter.mode == 'limit_battery_charge'


def test_mqtt_force_charge_publishes_force_charge_mode_and_rate(
    activated_mqtt_inverter,
):
    inverter, mock_client = activated_mqtt_inverter

    inverter.set_mode_force_charge(3000)

    assert call('inverter/command/mode', 'force_charge', qos=1, retain=False) in (
        mock_client.publish.call_args_list
    )
    assert call('inverter/command/charge_rate', '3000', qos=1, retain=False) in (
        mock_client.publish.call_args_list
    )


def test_mqtt_avoid_discharge_publishes_avoid_discharge_mode(
    activated_mqtt_inverter,
):
    inverter, mock_client = activated_mqtt_inverter

    inverter.set_mode_avoid_discharge()

    mock_client.publish.assert_called_once_with(
        'inverter/command/mode',
        'avoid_discharge',
        qos=1,
        retain=False,
    )


def test_mqtt_allow_discharge_publishes_allow_discharge_mode(
    activated_mqtt_inverter,
):
    inverter, mock_client = activated_mqtt_inverter

    inverter.set_mode_allow_discharge()

    mock_client.publish.assert_called_once_with(
        'inverter/command/mode',
        'allow_discharge',
        qos=1,
        retain=False,
    )


def test_mqtt_limit_battery_charge_publishes_limit_mode_and_rate(
    activated_mqtt_inverter,
):
    inverter, mock_client = activated_mqtt_inverter

    inverter.set_mode_limit_battery_charge(2000)

    assert call(
        'inverter/command/mode',
        'limit_battery_charge',
        qos=1,
        retain=False,
    ) in mock_client.publish.call_args_list
    assert call(
        'inverter/command/limit_battery_charge_rate',
        '2000',
        qos=1,
        retain=False,
    ) in mock_client.publish.call_args_list
