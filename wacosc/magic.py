from typing import TYPE_CHECKING
import liblo
import logging


if TYPE_CHECKING:
    from wacosc.osc import OSCInterface


log = logging.getLogger(__name__)


class MagicHandler:
    def __init__(self, osc: 'OSCInterface', kind: str, key: str, config: dict):
        self.osc = osc
        self.kind = kind  # eg stylus
        self.key = key  # eg tilx_x
        self.config = config

    def plug(self, config: dict, value: int | str):
        from wacosc.recorder import RecorderInterface
        if isinstance(self.osc, RecorderInterface):
            return (self.kind, self.key, value)
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
            log.exception(e)

    def __call__(self, value):
        """Here's where the magic happens"""
        log.info(self.key, value, self.config)
        
        if hasattr(self.config, 'values') and isinstance(list(self.config.values())[0], dict):
            for subkey, cfg in self.config.items():
                try:
                    if value:
                        self.osc.send(*self.plug(cfg, value))
                except TypeError as ex:
                    log.debug(str(ex))
        else:
            try:
                self.osc.send(*self.plug(self.config, value))
            except TypeError as ex:
                log.debug(str(ex))
