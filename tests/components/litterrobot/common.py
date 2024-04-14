"""Common utils for Litter-Robot tests."""

from homeassistant.components.litterrobot import DOMAIN
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME

BASE_PATH = "homeassistant.components.litterrobot"
CONFIG = {DOMAIN: {CONF_USERNAME: "user@example.com", CONF_PASSWORD: "password"}}

ROBOT_NAME = "Test"
ROBOT_SERIAL = "LR3C012345"
ROBOT_DATA = {
    "powerStatus": "AC",
    "lastSeen": "2022-09-17T13:06:37.884Z",
    "cleanCycleWaitTimeMinutes": "7",
    "unitStatus": "RDY",
    "litterRobotNickname": ROBOT_NAME,
    "cycleCount": "15",
    "panelLockActive": "0",
    "cyclesAfterDrawerFull": "0",
    "litterRobotSerial": ROBOT_SERIAL,
    "cycleCapacity": "30",
    "litterRobotId": "a0123b4567cd8e",
    "nightLightActive": "1",
    "sleepModeActive": "112:50:19",
}
ROBOT_4_DATA = {
    "name": ROBOT_NAME,
    "serial": "LR4C010001",
    "userId": "1234567",
    "espFirmware": "1.1.50",
    "picFirmwareVersion": "10512.2560.2.53",
    "laserBoardFirmwareVersion": "4.0.65.4",
    "wifiRssi": -53.0,
    "unitPowerType": "AC",
    "catWeight": 12.0,
    "displayCode": "DC_MODE_IDLE",
    "unitTimezone": "America/New_York",
    "unitTime": None,
    "cleanCycleWaitTime": 15,
    "isKeypadLockout": False,
    "nightLightMode": "OFF",
    "nightLightBrightness": 85,
    "isPanelSleepMode": False,
    "panelSleepTime": 0,
    "panelWakeTime": 0,
    "weekdaySleepModeEnabled": {
        "Sunday": {"sleepTime": 0, "wakeTime": 0, "isEnabled": False},
        "Monday": {"sleepTime": 0, "wakeTime": 180, "isEnabled": True},
        "Tuesday": {"sleepTime": 0, "wakeTime": 180, "isEnabled": True},
        "Wednesday": {"sleepTime": 0, "wakeTime": 180, "isEnabled": True},
        "Thursday": {"sleepTime": 0, "wakeTime": 180, "isEnabled": True},
        "Friday": {"sleepTime": 0, "wakeTime": 180, "isEnabled": True},
        "Saturday": {"sleepTime": 0, "wakeTime": 0, "isEnabled": False},
    },
    "unitPowerStatus": "ON",
    "sleepStatus": "WAKE",
    "robotStatus": "ROBOT_IDLE",
    "globeMotorFaultStatus": "FAULT_CLEAR",
    "pinchStatus": "CLEAR",
    "catDetect": "CAT_DETECT_CLEAR",
    "isBonnetRemoved": False,
    "isNightLightLEDOn": False,
    "odometerPowerCycles": 8,
    "odometerCleanCycles": 158,
    "odometerEmptyCycles": 1,
    "odometerFilterCycles": 0,
    "isDFIResetPending": False,
    "DFINumberOfCycles": 104,
    "DFILevelPercent": 76,
    "isDFIFull": False,
    "DFIFullCounter": 3,
    "DFITriggerCount": 42,
    "litterLevel": 460,
    "DFILevelMM": 115,
    "isCatDetectPending": False,
    "globeMotorRetractFaultStatus": "FAULT_CLEAR",
    "robotCycleStatus": "CYCLE_IDLE",
    "robotCycleState": "CYCLE_STATE_WAIT_ON",
    "weightSensor": -3.0,
    "isOnline": True,
    "isOnboarded": True,
    "isProvisioned": True,
    "isDebugModeActive": False,
    "lastSeen": "2022-09-17T12:06:37.884Z",
    "sessionId": "abcdef12-e358-4b6c-9022-012345678912",
    "setupDateTime": "2022-08-28T17:01:12.644Z",
    "isFirmwareUpdateTriggered": False,
    "firmwareUpdateStatus": "NONE",
    "wifiModeStatus": "ROUTER_CONNECTED",
    "isUSBPowerOn": True,
    "USBFaultStatus": "CLEAR",
    "isDFIPartialFull": True,
}
FEEDER_ROBOT_DATA = {
    "id": 1,
    "name": ROBOT_NAME,
    "serial": "RF1C000001",
    "timezone": "America/Denver",
    "isEighthCupEnabled": False,
    "created_at": "2021-12-15T06:45:00.000000+00:00",
    "household_id": 1,
    "state": {
        "id": 1,
        "info": {
            "level": 2,
            "power": True,
            "online": True,
            "acPower": True,
            "dcPower": False,
            "gravity": False,
            "chuteFull": False,
            "fwVersion": "1.0.0",
            "onBoarded": True,
            "unitMeals": 0,
            "motorJammed": False,
            "chuteFullExt": False,
            "panelLockout": False,
            "unitPortions": 0,
            "autoNightMode": True,
            "mealInsertSize": 1,
        },
        "updated_at": "2022-09-08T15:07:00.000000+00:00",
    },
    "feeding_snack": [
        {"timestamp": "2022-09-04T03:03:00.000000+00:00", "amount": 0.125},
        {"timestamp": "2022-08-30T16:34:00.000000+00:00", "amount": 0.25},
    ],
    "feeding_meal": [
        {
            "timestamp": "2022-09-08T18:00:00.000000+00:00",
            "amount": 0.125,
            "meal_name": "Lunch",
            "meal_number": 2,
            "meal_total_portions": 2,
        },
        {
            "timestamp": "2022-09-08T12:00:00.000000+00:00",
            "amount": 0.125,
            "meal_name": "Breakfast",
            "meal_number": 1,
            "meal_total_portions": 1,
        },
    ],
}

VACUUM_ENTITY_ID = "vacuum.test_litter_box"


async def remove_device(ws_client, device_id, config_entry_id):
    """Remove config entry from a device."""
    await ws_client.send_json(
        {
            "id": 5,
            "type": "config/device_registry/remove_config_entry",
            "config_entry_id": config_entry_id,
            "device_id": device_id,
        }
    )
    response = await ws_client.receive_json()
    return response["success"]
