from fastapi import FastAPI
from src.ilo import ilo_api

app = FastAPI()


@app.get("/api_health")
async def read_health():
    return {"status": "healthy"}


@app.get("/")
async def root():
    return {
        "Power State": "/power_state",
        "Power ON": "/power_on",
        "Power OFF": "/power_off",
        "Restart": "/restart",
        "Push Power Button": "/push_power_button",
        "Get Info": "/get_info",
        "Custom API call": {
            "path": "/custom/{method}/{path}?headers={headers}&body={body}&raw={raw}",
            "raw": ["true", "false"],
            "description": "Custom call to redfish api backend. Headers and body are optional",
            "example": "http://<URL>/custom/get/redfish/v1/Systems/1"
        }
    }


@app.get("/power_on")
async def power_on():
    return ilo_api.power_on()


@app.get("/power_off")
async def power_off():
    return ilo_api.power_off()


@app.get("/get_info")
async def get_info():
    return ilo_api.get_info()


@app.get("/power_state")
async def power_state():
    return {'PowerState': ilo_api.get_info()['PowerState']}


@app.get("/restart")
async def restart():
    return ilo_api.restart()


@app.get("/push_power_button")
async def push_power_button():
    return ilo_api.push_power_button()


@app.get("/custom/{method}/{api_path:path}")
async def custom_api_call(api_path: str = None, method: str = None, headers: dict = None, body: dict = None, raw: bool = False):
    try:
        response = ilo_api.custom_api_call(api_path, method, headers, body, raw)
    except Exception as e:
        return {
            'error': 'invalid request',
            'exception': str(e),
            'recommendation': 'Check the request parameters'
        }
    return response
