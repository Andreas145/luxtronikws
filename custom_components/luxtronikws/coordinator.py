from .config_flow import getWebsocket
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
)
from homeassistant.core import HomeAssistant
from datetime import timedelta
import async_timeout
import logging
import xml.etree.ElementTree as ET

_LOGGER = logging.getLogger(__name__)


class LuxtronikCoordinator(DataUpdateCoordinator):
    """Luxtronik custom coordinator."""

    def __init__(self, hass: HomeAssistant, server, password, update_interval) -> None:
        """Initialize my coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            # Name of the data. For logging purposes.
            name="LuxtronikCoordinator",
            # Polling interval. Will only be polled if there are subscribers.
            update_interval=timedelta(seconds=update_interval),
        )
        self._attr_server = server
        self._attr_password = password

    async def _ainit(self) -> None:
        ws, root, _, _ = await getWebsocket(self._attr_server, self._attr_password)
        self._attr_ws = ws
        self._attr_root = root

    async def _async_update_data(self):
        """Fetch data from API endpoint.

        This is the place to pre-process the data to lookup tables
        so entities can quickly look up their data.
        """
        # Note: asyncio.TimeoutError and aiohttp.ClientError are already
        # handled by the data update coordinator.
        async with async_timeout.timeout(10):
            await self._ainit()
            """
            # send ws queries for item ids
            listedItems = list(list(self._attr_root)[1])

            await self._attr_ws.send("GET;"+listedItems[2].attrib["id"])
            result = await self._attr_ws.recv()
            tempsettingsroot = ET.fromstring(result)
            """
            
            listedItems = list(list(self._attr_root)[0])

            await self._attr_ws.send("GET;"+listedItems[1].attrib["id"])
            result = await self._attr_ws.recv()
            tempsroot = ET.fromstring(result)

            await self._attr_ws.send("GET;"+listedItems[2].attrib["id"])
            result = await self._attr_ws.recv()
            inputsroot = ET.fromstring(result)

            await self._attr_ws.send("GET;"+listedItems[3].attrib["id"])
            result = await self._attr_ws.recv()
            outputsroot = ET.fromstring(result)

            await self._attr_ws.send("GET;"+listedItems[4].attrib["id"])
            result = await self._attr_ws.recv()
            timesroot = ET.fromstring(result)

            await self._attr_ws.send("GET;"+listedItems[5].attrib["id"])
            result = await self._attr_ws.recv()
            hoursroot = ET.fromstring(result)

            await self._attr_ws.send("GET;"+listedItems[8].attrib["id"])
            result = await self._attr_ws.recv()
            deviceinforoot = ET.fromstring(result)

            await self._attr_ws.send("GET;"+listedItems[9].attrib["id"])
            result = await self._attr_ws.recv()
            energyOutroot = ET.fromstring(result)

            await self._attr_ws.send("GET;"+listedItems[10].attrib["id"])
            result = await self._attr_ws.recv()
            energyInroot = ET.fromstring(result)

            await(self._attr_ws.close())

            return {
                "temperatures": tempsroot,
                "inputs": inputsroot,
                "outputs": outputsroot,
                "deviceinfo": deviceinforoot,
                "times": timesroot,
                "hours": hoursroot,
                "energyOutputs": energyOutroot,
                "energyInputs": energyInroot,
                # "tempSettings": tempsettingsroot,
            }
            # globber results to dict
            # return result data

    def appendXMLListToDictList(self, typeValue, swValue, xmlList, dict, groupName, maxIndex=99, *args):
        i = 0
        for item in xmlList:
            sublist = list(item)
            if len(sublist) == 2 and (len(args) == 0 or sublist[1].text.endswith(args[0])):
                dict.append({"type": typeValue, "sw": swValue, "name": sublist[0].text, "index": i, "group": groupName })

            i = i + 1
            if i > maxIndex:
                return

    def listEntities(self):
        root = self.data["deviceinfo"]
        
        listed = list(root)

        typeValue = list(listed[1])[1].text
        swValue = list(listed[2])[1].text
        # stateName = list(listed[6])[1].text
        # capacityName = "-/-"

        # stringDicts = [{"type": typeValue, "sw": swValue, "name": stateName, "index": 7, "group": "deviceinfo" }]
        stringDicts = []
        # powerDicts = [{"type": typeValue, "sw": swValue, "name": capacityName, "index": 8, "group": "deviceinfo" }]
        powerDicts = []
        
        listed = list(self.data["temperatures"])
        tempDicts = []
        self.appendXMLListToDictList(typeValue, swValue, listed, tempDicts, "temperatures")
        """
        listed = list(self.data["tempSettings"])
        tempDicts.append({"type": typeValue, "sw": swValue, "name": list(listed[1])[0].text, "index": 1, "group": "tempSettings" })
        tempDicts.append({"type": typeValue, "sw": swValue, "name": list(listed[2])[0].text, "index": 2, "group": "tempSettings" })
        """
        listed = list(self.data["inputs"])
        pressureDicts = []
        pressureDicts.append({"type": typeValue, "sw": swValue, "name": list(listed[6])[0].text, "index": 6, "group": "inputs" })
        pressureDicts.append({"type": typeValue, "sw": swValue, "name": list(listed[7])[0].text, "index": 7, "group": "inputs" })
        self.appendXMLListToDictList(typeValue, swValue, listed, stringDicts, "inputs", 4)

        listed = list(self.data["outputs"])
        # frequencyDicts = [{"type": typeValue, "sw": swValue, "name": list(listed[10])[0].text, "index": 10, "group": "outputs" }]
        frequencyDicts = []
        percentageDicts = []
        self.appendXMLListToDictList(typeValue, swValue, listed, stringDicts, "outputs", 15)
        percentageDicts.append({"type": typeValue, "sw": swValue, "name": list(listed[16])[0].text, "index": 16, "group": "outputs" })
        percentageDicts.append({"type": typeValue, "sw": swValue, "name": list(listed[17])[0].text, "index": 17, "group": "outputs" })
        stringDicts.append({"type": typeValue, "sw": swValue, "name": list(listed[18])[0].text, "index": 18, "group": "outputs" })

        listed = list(self.data["energyOutputs"])
        energyDicts = []
        energyDicts.append({"type": typeValue, "sw": swValue, "name": list(listed[1])[0].text+" (output)", "index": 1, "group": "energyOutputs" })
        energyDicts.append({"type": typeValue, "sw": swValue, "name": list(listed[2])[0].text+" (output)", "index": 2, "group": "energyOutputs" })
        energyDicts.append({"type": typeValue, "sw": swValue, "name": list(listed[3])[0].text+" (output)", "index": 3, "group": "energyOutputs" })
        energyDicts.append({"type": typeValue, "sw": swValue, "name": list(listed[4])[0].text+" (output)", "index": 4, "group": "energyOutputs" })

        listed = list(self.data["energyInputs"])
        energyDicts.append({"type": typeValue, "sw": swValue, "name": list(listed[1])[0].text+" (input)", "index": 1, "group": "energyInputs" })
        energyDicts.append({"type": typeValue, "sw": swValue, "name": list(listed[2])[0].text+" (input)", "index": 2, "group": "energyInputs" })
        energyDicts.append({"type": typeValue, "sw": swValue, "name": list(listed[3])[0].text+" (input)", "index": 3, "group": "energyInputs" })
        energyDicts.append({"type": typeValue, "sw": swValue, "name": list(listed[4])[0].text+" (input)", "index": 4, "group": "energyInputs" })

        listed = list(self.data["times"])
        timeDicts = []
        self.appendXMLListToDictList(typeValue, swValue, listed, timeDicts, "times")

        listed = list(self.data["hours"])
        hourDicts = []
        self.appendXMLListToDictList(typeValue, swValue, listed, hourDicts, "hours", 99, "h")
        counterDicts = [{"type": typeValue, "sw": swValue, "name": list(listed[2])[0].text, "index": 2, "group": "hours" }]
        timeDicts.append({"type": typeValue, "sw": swValue, "name": list(listed[3])[0].text, "index": 3, "group": "hours" })
        # counterDicts = []
        
        return {
            "tempDicts": tempDicts,
            "pressureDicts": pressureDicts,
            "frequencyDicts": frequencyDicts,
            "percentageDicts": percentageDicts,
            "powerDicts": powerDicts,
            "energyDicts": energyDicts,
            "timeDicts": timeDicts,
            "stringDicts": stringDicts,
            "hourDicts": hourDicts,
            "counterDicts": counterDicts
        }
