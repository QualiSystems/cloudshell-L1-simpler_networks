import os

from cloudshell.layer_one.core.helper.runtime_configuration import RuntimeConfiguration
from simpler_networks.snmp.read_write_snmp_handler import ReadWriteSnmpHandler
from simpler_networks.snmp.read_write_snmp_parameters import ReadWriteSNMPV2Parameters


class SnmpHandlerFactory(object):
    SIMPLER_NETWORKS_MIB = 'SIMPLER-NETWORKS-MIB'

    def __init__(self, host, logger):
        self._logger = logger
        self._snmp_handler = self._init_snmp_handler(
            ReadWriteSNMPV2Parameters(host, RuntimeConfiguration().read_key('SNMP.READ_COMMUNITY'),
                                      RuntimeConfiguration().read_key('SNMP.WRITE_COMMUNITY')))

    def _init_snmp_handler(self, snmp_parameters):
        snmp_handler = ReadWriteSnmpHandler(snmp_parameters, self._logger)

        path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'mibs'))
        snmp_handler.update_mib_sources(path)
        snmp_handler.load_mib(self.SIMPLER_NETWORKS_MIB)
        return snmp_handler

    def snmp_handler(self):
        """
        SNMP write handler
        :return:
        :rtype: simpler_networks.snmp.read_write_snmp_handler.ReadWriteSnmpHandler

        """
        return self._snmp_handler
