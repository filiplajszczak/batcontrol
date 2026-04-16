from unittest.mock import MagicMock, call, patch

import pytest

from batcontrol.inverter.fronius_modbus_tcp_transport import FroniusModbusTcpTransport
from batcontrol.inverter.fronius_modbus_types import RegisterRead, RegisterWrite


def test_transport_reads_holding_registers_via_modbus_client():
    mock_client = MagicMock()
    mock_client.read_holding_registers.return_value = [10240, 0, 0]

    with patch(
        "batcontrol.inverter.fronius_modbus_tcp_transport.ModbusTCPClient",
        return_value=mock_client,
    ):
        transport = FroniusModbusTcpTransport("192.168.1.100", port=502, unit_id=1)

    result = transport.read_registers(40345, 3)

    assert result == RegisterRead(start_register=40345, values=[10240, 0, 0])
    mock_client.read_holding_registers.assert_called_once_with(40345, 3)


def test_transport_writes_registers_in_order_via_modbus_client():
    mock_client = MagicMock()

    with patch(
        "batcontrol.inverter.fronius_modbus_tcp_transport.ModbusTCPClient",
        return_value=mock_client,
    ):
        transport = FroniusModbusTcpTransport("192.168.1.100", port=502, unit_id=1)

    transport.write_registers(
        [
            RegisterWrite(40360, 1),
            RegisterWrite(40358, 900),
            RegisterWrite(40355, 59536),
        ]
    )

    assert mock_client.write_register.call_args_list == [
        call(40360, 1),
        call(40358, 900),
        call(40355, 59536),
    ]


def test_transport_connects_client_on_initialization():
    mock_client = MagicMock()

    with patch(
        "batcontrol.inverter.fronius_modbus_tcp_transport.ModbusTCPClient",
        return_value=mock_client,
    ):
        FroniusModbusTcpTransport("192.168.1.100", port=1502, unit_id=3)

    mock_client.connect.assert_called_once_with()


def test_transport_passes_host_port_and_unit_id_to_modbus_client():
    with patch("batcontrol.inverter.fronius_modbus_tcp_transport.ModbusTCPClient") as mock_cls:
        FroniusModbusTcpTransport("192.168.1.100", port=1502, unit_id=3)

    mock_cls.assert_called_once_with("192.168.1.100", port=1502, slave_id=3)


def test_transport_close_closes_modbus_client():
    mock_client = MagicMock()

    with patch(
        "batcontrol.inverter.fronius_modbus_tcp_transport.ModbusTCPClient",
        return_value=mock_client,
    ):
        transport = FroniusModbusTcpTransport("192.168.1.100", port=502, unit_id=1)

    transport.close()

    mock_client.close.assert_called_once_with()


def test_transport_rejects_empty_write_batch():
    mock_client = MagicMock()

    with patch(
        "batcontrol.inverter.fronius_modbus_tcp_transport.ModbusTCPClient",
        return_value=mock_client,
    ):
        transport = FroniusModbusTcpTransport("192.168.1.100", port=502, unit_id=1)

    with pytest.raises(ValueError, match="writes must not be empty"):
        transport.write_registers([])
