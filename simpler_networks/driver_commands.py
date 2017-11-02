#!/usr/bin/python
# -*- coding: utf-8 -*-

from cloudshell.layer_one.core.driver_commands_interface import DriverCommandsInterface
from cloudshell.layer_one.core.layer_one_driver_exception import LayerOneDriverException
from cloudshell.layer_one.core.response.resource_info.entities.attributes import StringAttribute
from cloudshell.layer_one.core.response.response_info import ResourceDescriptionResponseInfo, GetStateIdResponseInfo
from simpler_networks.helpers.autoload_helper import AutoloadHelper
from simpler_networks.snmp.snmp_handler_factory import SnmpHandlerFactory


class DriverCommands(DriverCommandsInterface):
    SIMPLER_NETWORKS_MIB = 'SIMPLER-NETWORKS-MIB'
    """
    Driver commands implementation
    """

    def __init__(self, logger):
        """
        :param logger:
        :type logger: logging.Logger
        """
        self._logger = logger
        self.__snmp_handler_factory = None

    @property
    def _snmp_handler_factory(self):
        """
        SNMP handler factory
        :return:
        :rtype: simpler_networks.snmp.snmp_handler_factory.SnmpHandlerFactory
        """
        if self.__snmp_handler_factory:
            return self.__snmp_handler_factory
        raise LayerOneDriverException(self.__class__.__name__,
                                      'SNMP factory called before initialization')

    @_snmp_handler_factory.setter
    def _snmp_handler_factory(self, value):
        self.__snmp_handler_factory = value

    @property
    def snmp_handler(self):
        return self._snmp_handler_factory.snmp_handler()

    @property
    def card_table(self):
        return self.snmp_handler.walk((self.SIMPLER_NETWORKS_MIB, 'sniEntityCardTable'))

    @property
    def port_table(self):
        return self.snmp_handler.walk((self.SIMPLER_NETWORKS_MIB, 'sniEntityPortTable'))

    @property
    def connection_table(self):
        return self.snmp_handler.walk((self.SIMPLER_NETWORKS_MIB, 'sniConnTable'))

    @property
    def chassis_sn(self):
        return self.snmp_handler.get((self.SIMPLER_NETWORKS_MIB, 'sniEntitySysImageVersion')).get(
            'sniEntitySysImageVersion')

    def login(self, address, username, password):
        """
        Perform login operation on the device
        :param address: resource address, "192.168.42.240"
        :param username: username to login on the device
        :param password: password
        :return: None
        :raises Exception: if command failed
        Example:
            # Define session attributes
            self._cli_handler.define_session_attributes(address, username, password)

            # Obtain cli session
            with self._cli_handler.default_mode_service() as session:
                # Executing simple command
                device_info = session.send_command('show version')
                self._logger.info(device_info)
        """
        self._snmp_handler_factory = SnmpHandlerFactory(address, self._logger)
        sys_descr = self.snmp_handler.get(('SNMPv2-MIB', 'sysDescr', '0')).get('sysDescr')
        self._logger.info('Connected to ' + sys_descr)

    def get_state_id(self):
        """
        Check if CS synchronized with the device.
        :return: Synchronization ID, GetStateIdResponseInfo(-1) if not used
        :rtype: cloudshell.layer_one.core.response.response_info.GetStateIdResponseInfo
        :raises Exception: if command failed

        Example:
            # Obtain cli session
            with self._cli_handler.default_mode_service() as session:
                # Execute command
                chassis_name = session.send_command('show chassis name')
                return chassis_name
        """
        return GetStateIdResponseInfo(self.snmp_handler.get(('SNMPv2-MIB', 'sysName')).get('sysName'))

    def set_state_id(self, state_id):
        """
        Set synchronization state id to the device, called after Autoload or SyncFomDevice commands
        :param state_id: synchronization ID
        :type state_id: str
        :return: None
        :raises Exception: if command failed

        Example:
            # Obtain cli session
            with self._cli_handler.config_mode_service() as session:
                # Execute command
                session.send_command('set chassis name {}'.format(state_id))
        """
        self.snmp_handler.set([(('SNMPv2-MIB', 'sysName', '0'), str(state_id))])

    @staticmethod
    def _src_port_index(index):
        return 0 < int(index) <= 50

    @staticmethod
    def _dst_port_index(index):
        return 100 < int(index) <= 116

    def _fix_port_order(self, *port_pair):
        if not len(port_pair) == 2:
            raise Exception(self.__class__.__name__, 'Only port pair can be handled')

        src_port = None
        dst_port = None
        for port in port_pair:
            if self._src_port_index(port[1]):
                src_port = port
            if self._dst_port_index(port[1]):
                dst_port = port

        if not src_port or not dst_port:
            raise Exception(self.__class__.__name__,
                            'Cannot map ports: {0}, {1}'.format('.'.join(port_pair[0]), '.'.join(port_pair[1])))
        return src_port, dst_port

    @staticmethod
    def _convert_port(cs_port):
        return tuple(cs_port.split('/')[1:])

    def map_bidi(self, src_port, dst_port):
        """
        Create a bidirectional connection between source and destination ports
        :param src_port: src port address, '192.168.42.240/1/21'
        :type src_port: str
        :param dst_port: dst port address, '192.168.42.240/1/22'
        :type dst_port: str
        :return: None
        :raises Exception: if command failed

        Example:
            with self._cli_handler.config_mode_service() as session:
                session.send_command('map bidir {0} {1}'.format(convert_port(src_port), convert_port(dst_port)))

        """

        self._logger.debug('Connecting ports {0}, {1}'.format(src_port, dst_port))
        src_tuple, dst_tuple = self._fix_port_order(self._convert_port(src_port), self._convert_port(dst_port))
        self._logger.debug('Connection order {0}, {1}'.format(src_tuple, dst_tuple))
        self.snmp_handler.set(
            [((self.SIMPLER_NETWORKS_MIB, 'sniConnRowStatus', src_tuple[0], src_tuple[1], dst_tuple[0],
               dst_tuple[1], '2'), '4')])

    def map_uni(self, src_port, dst_ports):
        """
        Unidirectional mapping of two ports
        :param src_port: src port address, '192.168.42.240/1/21'
        :type src_port: str
        :param dst_ports: list of dst ports addresses, ['192.168.42.240/1/22', '192.168.42.240/1/23']
        :type dst_ports: list
        :return: None
        :raises Exception: if command failed

        Example:
            with self._cli_handler.config_mode_service() as session:
                for dst_port in dst_ports:
                    session.send_command('map {0} also-to {1}'.format(convert_port(src_port), convert_port(dst_port)))
        """
        raise Exception(self.__class__.__name__, 'Unidirectional connections are not allowed')

    def get_resource_description(self, address):
        """
        Auto-load function to retrieve all information from the device
        :param address: resource address, '192.168.42.240'
        :type address: str
        :return: resource description
        :rtype: cloudshell.layer_one.core.response.response_info.ResourceDescriptionResponseInfo
        :raises cloudshell.layer_one.core.layer_one_driver_exception.LayerOneDriverException: Layer one exception.

        Example:

            from cloudshell.layer_one.core.response.resource_info.entities.chassis import Chassis
            from cloudshell.layer_one.core.response.resource_info.entities.blade import Blade
            from cloudshell.layer_one.core.response.resource_info.entities.port import Port

            chassis_resource_id = chassis_info.get_id()
            chassis_address = chassis_info.get_address()
            chassis_model_name = "Simpler Networks Chassis"
            chassis_serial_number = chassis_info.get_serial_number()
            chassis = Chassis(resource_id, address, model_name, serial_number)

            blade_resource_id = blade_info.get_id()
            blade_model_name = 'Generic L1 Module'
            blade_serial_number = blade_info.get_serial_number()
            blade.set_parent_resource(chassis)

            port_id = port_info.get_id()
            port_serial_number = port_info.get_serial_number()
            port = Port(port_id, 'Generic L1 Port', port_serial_number)
            port.set_parent_resource(blade)

            return ResourceDescriptionResponseInfo([chassis])
        """
        from cards import CARDS
        from ports import PORTS
        # snmp_handler = self._snmp_handler_factory.snmp_handler()

        # connection_table = snmp_handler.walk((self.SIMPLER_NETWORKS_MIB, 'sniConnTable'))
        connection_table = self.connection_table
        # port_table = snmp_handler.walk((self.SIMPLER_NETWORKS_MIB, 'sniEntityPortTable'))
        port_table = PORTS
        # card_table = snmp_handler.walk((self.SIMPLER_NETWORKS_MIB, 'sniEntityCardTable'))
        card_table = CARDS

        # resource_descr = snmp_handler.get(('SNMPv2-MIB', 'sysDescr', '0')).get('sysDescr')
        resource_descr = 'SN'
        response_info = ResourceDescriptionResponseInfo(
            AutoloadHelper(address, resource_descr, self.chassis_sn, card_table, port_table, connection_table,
                           self._logger).build_structure())
        return response_info

    @staticmethod
    def convert_connection_table(conn_table):
        connection_dict = {}
        for conn_data in conn_table.values():
            from_card = conn_data.get('sniConnFromEndPointCard')
            from_port = conn_data.get('sniConnFromEndPointPort')
            to_card = conn_data.get('sniConnToEndPointCard')
            to_port = conn_data.get('sniConnToEndPointPort')
            connection_dict[(from_card, from_port)] = (to_card, to_port)
        return connection_dict

    def map_clear(self, ports):
        """
        Remove simplex/multi-cast/duplex connection ending on the destination port
        :param ports: ports, ['192.168.42.240/1/21', '192.168.42.240/1/22']
        :type ports: list
        :return: None
        :raises Exception: if command failed

        Example:
            with self._cli_handler.config_mode_service() as session:
            for port in ports:
                session.send_command('map clear {}'.format(convert_port(port)))
        """
        connection_table = self.convert_connection_table(self.connection_table)
        connection_table_by_value = {v: k for k, v in connection_table.iteritems()}

        for cs_port in ports:
            port = self._convert_port(cs_port)
            src_port = None
            dst_port = None
            if port in connection_table:
                src_port = port
                dst_port = connection_table.get(port)
            elif port in connection_table_by_value:
                src_port = connection_table_by_value.get(port)
                dst_port = port
            if src_port and dst_port:
                self._unmap_ports(src_port, dst_port)

    def _unmap_ports(self, src_port, dst_port):
        src_port, dst_port = self._fix_port_order(src_port, dst_port)
        self._logger.debug('Clear order {0}, {1}'.format(src_port, dst_port))
        self.snmp_handler.set(
            [((self.SIMPLER_NETWORKS_MIB, 'sniConnRowStatus', src_port[0], src_port[1], dst_port[0],
               dst_port[1], '2'), '6')])

    def map_clear_to(self, src_port, dst_ports):
        """
        Remove simplex/multi-cast/duplex connection ending on the destination port
        :param src_port: src port address, '192.168.42.240/1/21'
        :type src_port: str
        :param dst_ports: list of dst ports addresses, ['192.168.42.240/1/21', '192.168.42.240/1/22']
        :type dst_ports: list
        :return: None
        :raises Exception: if command failed

        Example:
            with self._cli_handler.config_mode_service() as session:
                _src_port = convert_port(src_port)
                for port in dst_ports:
                    _dst_port = convert_port(port)
                    session.send_command('map clear-to {0} {1}'.format(_src_port, _dst_port))
        """

        self._logger.debug('Clear connection {0}, {1}'.format(src_port, dst_ports))
        self._unmap_ports(self._convert_port(src_port), self._convert_port(dst_ports[0]))

    def get_attribute_value(self, cs_address, attribute_name):
        """
        Retrieve attribute value from the device
        :param cs_address: address, '192.168.42.240/1/21'
        :type cs_address: str
        :param attribute_name: attribute name, "Port Speed"
        :type attribute_name: str
        :return: attribute value
        :rtype: cloudshell.layer_one.core.response.response_info.AttributeValueResponseInfo
        :raises Exception: if command failed

        Example:
            with self._cli_handler.config_mode_service() as session:
                command = AttributeCommandFactory.get_attribute_command(cs_address, attribute_name)
                value = session.send_command(command)
                return AttributeValueResponseInfo(value)
        """
        serial_number = 'Serial Number'
        if len(cs_address.split('/')) == 1 and attribute_name == serial_number:
            return StringAttribute(serial_number, self.chassis_sn or StringAttribute.DEFAULT_VALUE)
        else:
            raise Exception(self.__class__.__name__,
                            'Attribute {0} for {1} not available'.format(attribute_name, cs_address))

    def set_attribute_value(self, cs_address, attribute_name, attribute_value):
        """
        Set attribute value to the device
        :param cs_address: address, '192.168.42.240/1/21'
        :type cs_address: str
        :param attribute_name: attribute name, "Port Speed"
        :type attribute_name: str
        :param attribute_value: value, "10000"
        :type attribute_value: str
        :return: attribute value
        :rtype: cloudshell.layer_one.core.response.response_info.AttributeValueResponseInfo
        :raises Exception: if command failed

        Example:
            with self._cli_handler.config_mode_service() as session:
                command = AttributeCommandFactory.set_attribute_command(cs_address, attribute_name, attribute_value)
                session.send_command(command)
                return AttributeValueResponseInfo(attribute_value)
        """
        raise NotImplementedError

    def map_tap(self, src_port, dst_ports):
        return self.map_uni(src_port, dst_ports)
