import os

from cloudshell.layer_one.core.helper.runtime_configuration import RuntimeConfiguration
from cloudshell.snmp.quali_snmp import QualiSnmp
from cloudshell.snmp.snmp_parameters import SNMPV2ReadParameters, SNMPV2WriteParameters


class SnmpHandlerFactory(object):
    SIMPLER_NETWORKS_MIB = 'SIMPLER-NETWORKS-MIB'

    def __init__(self, host, logger):
        self._host = host
        self._logger = logger
        self._read_handler = self._init_read_handler()
        self._write_handler = self._init_write_handler()

    def _init_snmp_handler(self, snmp_parameters):
        snmp_handler = QualiSnmp(snmp_parameters, self._logger)
        path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'mibs'))
        snmp_handler.update_mib_sources(path)
        snmp_handler.load_mib(self.SIMPLER_NETWORKS_MIB)
        return snmp_handler

    def _init_read_handler(self):
        read_parameters = SNMPV2ReadParameters(self._host, RuntimeConfiguration().read_key('SNMP.READ_COMMUNITY'))
        snmp_handler = self._init_snmp_handler(read_parameters)
        snmp_handler._test_snmp_agent()
        return snmp_handler

    def _init_write_handler(self):
        write_parameters = SNMPV2WriteParameters(self._host, RuntimeConfiguration().read_key('SNMP.WRITE_COMMUNITY'))
        return self._init_snmp_handler(write_parameters)

    def read_handler(self):
        """
        SNMP read handler
        :return:
        :rtype: cloudshell.snmp.quali_snmp.QualiSnmp
        """
        return self._read_handler

    def write_handler(self):
        """
        SNMP write handler
        :return:
        :rtype: cloudshell.snmp.quali_snmp.QualiSnmp
        """
        return self._write_handler
