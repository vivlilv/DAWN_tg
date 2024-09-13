import time
import httpx




capmonster_api_key = '456ccb8e3c6a15acb0ab2ee4f7e039c0'


async def solve_captcha(img_base64):
    async with httpx.AsyncClient() as client:
        url = 'https://api.capmonster.cloud/createTask'
        data = {
            "clientKey": capmonster_api_key,
            "task": {
                "type": "ImageToTextTask",
                "body": img_base64,
                "case": True,
                "capMonsterModule":"universal"
            }
        }

        response = await client.post(url, json=data)
        data = response.json()
        print(data)
        
        #waiting for solution
        time.sleep(10)
        task_id = data.get('taskId')
        params = {
        "clientKey":capmonster_api_key,
        "taskId": task_id
        }

        result = await client.post(url='https://api.capmonster.cloud/getTaskResult', json=params)
        solution = result.json().get('solution').get('text')
        
        print(solution)
        return solution












