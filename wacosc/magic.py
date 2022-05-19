import liblo
import logging


log = logging.getLogger(__name__)


class MagicHandler:
    def __init__(self, osc, kind, key, config):
        self.osc = osc
        self.kind = kind  # eg stylus
        self.key = key  # eg tilx_x
        self.config = config

    def plug(self, config, value):
        try:
            plugin_name = config['plugin_name']
            plugin = self.osc.plugin_by_name(plugin_name)
            if plugin is None:
                raise RuntimeError(f'plugin not instanced: {plugin_name}')
            parameter_name = config['parameter_name']
            parameter_id = plugin['ranges']['sad_name'][parameter_name]

            value = config['fn'](value)
            return plugin['_id'], parameter_id, value
        except Exception as e:
            print(str(e))

    def __call__(self, value):
        """Here's where the magic happens"""
        print(value, self.config)
        if isinstance(list(self.config.values())[0], dict):
            for subkey, cfg in self.config.items():
                try:
                    if value:
                        self.send(*self.plug(cfg, value))
                except TypeError as ex:
                    log.debug(str(ex))
        else:
            try:
                self.send(*self.plug(self.config, value))
            except TypeError as ex:
                log.debug(str(ex))

    def send(self, plugin_id, parameter_id, value, udp=True):
        liblo.send(
            self.osc.carla_addr_udp if udp else self.osc.carla_addr_tcp,
            f'/Carla/{plugin_id}/set_parameter_value',
            parameter_id,
            value,
        )
