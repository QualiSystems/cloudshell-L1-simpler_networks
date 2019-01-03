from cloudshell.layer_one.core.response.resource_info.entities.blade import Blade
from cloudshell.layer_one.core.response.resource_info.entities.chassis import Chassis
from cloudshell.layer_one.core.response.resource_info.entities.port import Port


class AutoloadHelper(object):
    def __init__(self, address, resource_descr, chassis_sn, card_table, port_table, connection_table, logger):
        self._address = address
        self._card_table = card_table
        self._port_table = port_table
        self._connection_table = connection_table
        self._logger = logger
        self._resource_descr = resource_descr
        self._chassis_sn = chassis_sn

    def _build_chassis(self):
        chassis = Chassis('1', self._address, 'Simpler Networks Chassis', self._chassis_sn)
        chassis.set_model_name(self._resource_descr)
        chassis.set_serial_number(self._chassis_sn)
        return chassis

    def _build_cards(self, chassis):
        self._logger.debug('Build Cards')
        cards = {}
        for card_data in self._card_table.values():
            card_type = card_data.get('sniEntityCardType')
            if card_type and card_type.strip("'") == 'funnelcard':
                card_index = card_data.get('sniEntityCardIndex')
                card_model = card_data.get('sniEntityCardAid')
                card_serial_num = card_data.get('sniEntityCardSerialNum')
                card = Blade(card_index, 'Generic L1 Module', card_serial_num)
                card.set_model_name(card_model)
                card.set_serial_number(card_serial_num)
                card.set_parent_resource(chassis)
                cards[card_index] = card
        return cards

    def _build_ports(self, cards):
        self._logger.debug('Build Ports')
        ports = {}
        for port_data in self._port_table.values():
            card_index = port_data.get('sniEntityPortCardIndex')
            if card_index in cards:
                card = cards.get(card_index)
                port_index = port_data.get('sniEntityPortIndex')
                # port_model = port_data.get('sniEntityPortAid')
                port = Port(port_index, 'Generic L1 Port', '')
                port_model = port_data.get('sniEntityPortAid')
                port.set_model_name(port_model)
                port.set_parent_resource(card)
                ports['{0}.{1}'.format(card_index, port_index)] = port
        return ports

    def _build_ports_mapping(self, ports):
        self._logger.debug('Build Port Mappings')
        for conn_data in self._connection_table.values():
            from_card = conn_data.get('sniConnFromEndPointCard')
            from_port = conn_data.get('sniConnFromEndPointPort')
            to_card = conn_data.get('sniConnToEndPointCard')
            to_port = conn_data.get('sniConnToEndPointPort')
            from_port = ports.get('{0}.{1}'.format(from_card, from_port))
            to_port = ports.get('{0}.{1}'.format(to_card, to_port))
            if from_port and to_port:
                from_port.add_mapping(to_port)
                to_port.add_mapping(from_port)

    def build_structure(self):
        chassis = self._build_chassis()
        cards = self._build_cards(chassis)
        ports = self._build_ports(cards)
        self._build_ports_mapping(ports)
        return [chassis]
