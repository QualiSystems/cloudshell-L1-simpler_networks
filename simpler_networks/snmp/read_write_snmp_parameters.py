from cloudshell.snmp.snmp_parameters import SNMPParameters


class ReadWriteSNMPV2Parameters(SNMPParameters):
    def __init__(self, ip, snmp_read_community, snm_write_community, port=161):
        """
        Represents parameters for an SMNPV2 connection
        :param str ip: The device IP
        :param str snmp_read_community: SNMP Read community
        :param int port: SNMP port to use
        """
        SNMPParameters.__init__(self, ip=ip, port=port)
        self.snmp_read_community = snmp_read_community
        self.snmp_write_community = snm_write_community
