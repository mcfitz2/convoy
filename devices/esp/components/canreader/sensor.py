import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import sensor
from esphome.const import  CONF_ID, UNIT_EMPTY, ICON_EMPTY

can_reader_sensor_ns = cg.esphome_ns.namespace('canreader')
CanReaderSensor = can_reader_sensor_ns.class_('CanReaderSensor', cg.)

CONF_SENSOR1 = "battery_voltage"
CONF_SENSOR2 = "distance_since_codes_cleared"

CONFIG_SCHEMA = cv.Schema({
    cv.GenerateID(): cv.declare_id(CanReaderSensor),
    cv.Optional(CONF_SENSOR1):
        sensor.sensor_schema(UNIT_EMPTY, ICON_EMPTY, 1).extend(),
    cv.Optional(CONF_SENSOR2):
        sensor.sensor_schema(UNIT_EMPTY, ICON_EMPTY, 1).extend(),
}).extend(cv.polling_component_schema('60s'))


def to_code(config):
    var = cg.new_Pvariable(config[CONF_ID])
    yield cg.register_component(var, config)

    if CONF_SENSOR1 in config:
        conf = config[CONF_SENSOR1]
        sens = yield sensor.new_sensor(conf)
        cg.add(var.set_sensor1(sens))
        
    if CONF_SENSOR2 in config:
        conf = config[CONF_SENSOR2]
        sens = yield sensor.new_sensor(conf)
        cg.add(var.set_sensor2(sens))