from pysnmp.entity.rfc3413.oneliner import cmdgen
from pysnmp.error import PySnmpError
from pysnmp.smi import view
from pysnmp.smi.rfc1902 import ObjectIdentity, ObjectType

from cloudshell.snmp.quali_snmp import QualiSnmp


class ReadWriteSnmpHandler(QualiSnmp):
    def __init__(self, snmp_parameters, logger, snmp_error_values=None):
        """
        :param snmp_parameters:
        :type snmp_parameters: simpler_networks.snmp.read_write_snmp_parameters.ReadWriteSNMPV2Parameters
        :param logger:
        """
        self._snmp_errors = None
        snmp_error_values = snmp_error_values or []
        self.set_snmp_errors(snmp_error_values)
        self.cmd_gen = cmdgen.CommandGenerator()
        self.mib_builder = self.cmd_gen.snmpEngine.msgAndPduDsp.mibInstrumController.mibBuilder
        self.mib_viewer = view.MibViewController(self.mib_builder)
        self.logger = logger
        self.is_read_only = False
        self.logger.info('QualiSnmp Creating SNMP Handler')
        ip = snmp_parameters.ip
        if ':' in ip:
            ip = ip.split(':')[0]
        self.target = cmdgen.UdpTransportTarget((ip, snmp_parameters.port))
        self.security = cmdgen.CommunityData(snmp_parameters.snmp_write_community)
        self.write_security = cmdgen.CommunityData(snmp_parameters.snmp_write_community)
        self._test_snmp_agent()

    def _write_command(self, cmd, *oids):
        """ Execute provided command with provided oids

        :param cmd: command to execute, i.e get
        :param oids: request oids, '1.3.6.1.2.1.1.2'
        """

        error_indication, error_status, error_index, self.var_binds = cmd(self.write_security,
                                                                          self.target,
                                                                          *oids)
        # Check for errors
        if error_indication:
            raise PySnmpError(error_indication)
        if error_status:
            raise PySnmpError(error_status)

    def set(self, oids):
        """SNMP Set operation.

        :param oids: list of oids to set. oid can be full dotted OID or (MIB, OID name, [index]).
            For example, the OID to get sysContact can by any of the following:
            ('SNMPv2-MIB', 'sysContact', 0)
            '1.3.6.1.2.1.1.4.0'
            snmp.set([(("CISCO-CONFIG-COPY-MIB", "ccCopyProtocol", 10), 1),
                      (("CISCO-CONFIG-COPY-MIB", "ccCopySourceFileType", 10), 1),
                      (("CISCO-CONFIG-COPY-MIB", "ccCopyDestFileType", 10), 3),
                      (("CISCO-CONFIG-COPY-MIB", "ccCopyServerAddress", 10), "10.212.95.180"),
                      (("CISCO-CONFIG-COPY-MIB", "ccCopyFileName", 10), "test_snmp_running_config_save"),
                      (("CISCO-CONFIG-COPY-MIB", "ccCopyVrfName", 10), "management"),
                      (("CISCO-CONFIG-COPY-MIB", "ccCopyEntryRowStatus", 10), 4)])
        """

        if self.is_read_only:
            raise Exception(self.__class__.__name__, "SNMP Read Community doesn't support snmp set command")

        object_identities = []
        for oid in oids:
            if type(oid) is list or type(oid) is tuple:
                oid_0 = list(oid)
                if len(oid_0) < 2:
                    raise Exception(self.__class__.__name__, "Missing oid or value data")

                if type(oid[0]) is list or type(oid[0]) is tuple:
                    if (len(oid_0[0])) < 3:
                        raise Exception(self.__class__.__name__, "Missing oid index")
                object_identities.append(ObjectType(ObjectIdentity(*oid_0[0]), oid[1]))
            else:
                raise Exception(self.__class__.__name__, "Wrong oids parameter")

        self._write_command(self.cmd_gen.setCmd, *object_identities)
