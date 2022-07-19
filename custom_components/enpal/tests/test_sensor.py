import unittest
import custom_components.enpal.sensor as sensor

class IPSensorTest(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.ipv4 = sensor.IPSensor(False)
        self.ipv6 = sensor.IPSensor(True)

    def test_validate_ipv4(self):
        assert sensor.validate_ipv4('192.168.0.1')
        assert sensor.validate_ipv4('123.123.123.123')
        assert not sensor.validate_ipv4('300.0.0.1')
        assert not sensor.validate_ipv4('300.0.0.-1')
        assert not sensor.validate_ipv4('2001:0db8:85a3:0000:0000:8a2e:0370:7334')
        assert not sensor.validate_ipv4('1.2.3')
        assert not sensor.validate_ipv4('1.2.3.4.5')
        assert not sensor.validate_ipv4('abc.def.ghi.jkl')
        assert not sensor.validate_ipv4('192.168.abc.def')
        assert not sensor.validate_ipv4('')

    def test_validate_ipv6(self):
        assert sensor.validate_ipv6('2001:db8::2:1')
        assert not sensor.validate_ipv6('2001::2:1')
        assert sensor.validate_ipv6('2001:0db8:85a3:0000:0000:8a2e:0370:7334')
        assert not sensor.validate_ipv6('2001:0db8:85a3:00000:0000:8a2e:0370:7334')
        assert not sensor.validate_ipv6('2001:0db8:85a3:0000:0000:8a2e:0370:ghij')
        assert not sensor.validate_ipv6('300.0.0.1')
        assert not sensor.validate_ipv6('300.0.0.-1')
        assert not sensor.validate_ipv6('192.168.0.1')
        assert not sensor.validate_ipv6('1.2.3')
        assert not sensor.validate_ipv6('1.2.3.4.5')
        assert not sensor.validate_ipv6('')

    async def test_update_ipv4(self):
        await self.ipv4.async_update()
        if self.ipv4.native_value == None:
            return # skip tests if no ipv4 address is found (dev is offline?)
        assert sensor.validate_ipv4(self.ipv4.native_value)

    async def test_update_ipv6(self):
        await self.ipv6.async_update()
        if self.ipv6.native_value == None:
            return # skip tests if no ipv6 address is found (dev is offline or uses only ipv4?)
        assert len(self.ipv6.native_value) > 5
        isv4 = sensor.validate_ipv4(self.ipv6.native_value)
        if not isv4:
            assert sensor.validate_ipv6(self.ipv6.native_value)
