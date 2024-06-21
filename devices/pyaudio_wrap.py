import pyaudio

class PyAudioDevice(object):
    def _get_devices(self):
        device_count = self._pyaudio.get_device_count()
        devices = [self._pyaudio.get_device_info_by_index(i) for i in range(device_count)]
        return devices
    
    def _filter_device_by_name(self, devices, name: str):
        matching_candidates = [m for m in devices if name == m["name"]]
        
        if len(matching_candidates) == 1:
            return matching_candidates[0]

        contained_candidates = [m for m in devices if name in m["name"]]
        if len(contained_candidates) > 1:
            raise ValueError(f"Multiple devices contain the name '{name}'.")
        
        if len(contained_candidates) == 1:
            return contained_candidates[0]
        
        raise ValueError(f"No device found with the name '{name}'.")

    def _get_default(self):
        raise NotImplementedError()

    def __init__(self, name=None):
        self._pyaudio = pyaudio.PyAudio()
        self._dev_info = self._get_default() if name is None else self._filter_device_by_name(self._get_devices(), name)