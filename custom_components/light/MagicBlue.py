import logging

import voluptuous as vol

# Import the device class from the component that you want to support
from homeassistant.components.light import ATTR_BRIGHTNESS, Light, PLATFORM_SCHEMA
from homeassistant.const import CONF_HOST, CONF_USERNAME, CONF_PASSWORD
import homeassistant.helpers.config_validation as cv


REQUIREMENTS = [
    'https://github.com/Betree/magicblue'
    '/archive/0.2.2.zip'
    '#magicblue==0.2.2']

_LOGGER = logging.getLogger(__name__)

# Validation of the user's configuration
# Host should be MAC Address
CONF_DEVICES = 'devices'
CONF_VERSION = 'version'

DEFAULT_VERSION = 10

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_DEVICES): vol.All(cv.ensure_list, [
        {
            vol.Required(CONF_HOST): cv.string,
            vol.Optional(CONF_VERSION,default=DEFAULT_VERSION): cv.positive_int,
        },
    ]),
}
)



def setup_platform(hass, config, add_devices, discovery_info=None):
    """Setup the Magic Blue platform."""
        
    from magicbluelib import magicblue

    # Assign configuration variables. The configuration check takes care they are
    # present. 
    host = config.get(CONF_HOST)
    version = config.get(CONF_VERSION)

    # Setup connection with devices/cloud
    bulb = MagicBlue(host,version)
    bulb.connect()

    # Verify that passed in configuration works
    if not bulb.is_connected():
        _LOGGER.error('Could not connect to Magic Blue Bulb')
        return False

    # Add devices
    add_devices(MagicBlue(light))
    

class MagicBlue(Light):
    """Representation of a MagicBlue Bulb."""

    def __init__(self, light):
        """Initialize an MagicBlue."""
        self._light = light
        self._name = light.name
        self._state = None
        self._brightness = None

    @property
    def name(self):
        """Return the display name of this light."""
        return self._name

    @property
    def brightness(self):
        """Brightness of the light (an integer in the range 1-255).
        This method is optional. Removing it indicates to Home Assistant
        that brightness is not supported for this light.
        """
        return self._brightness

    @property
    def is_on(self):
        """Return true if light is on."""
        return self._state

    def turn_on(self, **kwargs):
        """Instruct the light to turn on.

        You can skip the brightness part if your light does not support
        brightness control.
        """
        self._light.brightness = kwargs.get(ATTR_BRIGHTNESS, 255)
        self._light.turn_on()

    def turn_off(self, **kwargs):
        """Instruct the light to turn off."""
        self._light.turn_off()

    def update(self):
        """Fetch new state data for this light.
        This is the only method that should fetch new data for Home Assistant.
        """
        self._light.update()
        self._state = self._light.is_on()
        self._brightness = self._light.brightness
