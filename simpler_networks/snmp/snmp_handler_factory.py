from cloudshell.layer_one.core.helper.runtime_configuration import RuntimeConfiguration
from cloudshell.snmp.quali_snmp import QualiSnmp
from cloudshell.snmp.snmp_parameters import SNMPV2ReadParameters, SNMPV2WriteParameters


class SnmpHandlerFactory(object):
    def __init__(self, host, logger):
        self._logger = logger
        self._read_parameters = SNMPV2ReadParameters(host, RuntimeConfiguration().read_key('SNMP.READ_COMMUNITY'))
        self._write_parameters = SNMPV2WriteParameters(host, RuntimeConfiguration().read_key('SNMP.WRITE_COMMUNITY'))

        self._read_handler = None
        self._write_handler = None

    def read_handler(self):
        """
        SNMP read handler
        :return:
        :rtype: cloudshell.snmp.quali_snmp.QualiSnmp
        """
        if not self._read_handler:
            self._read_handler = QualiSnmp(self._read_parameters, self._logger)
        return self._read_handler

    def write_handler(self):
        """
        SNMP write handler
        :return:
        :rtype: cloudshell.snmp.quali_snmp.QualiSnmp
        """
        if not self._write_handler:
            self._write_handler = QualiSnmp(self._write_parameters, self._logger)
        return self._write_handler
