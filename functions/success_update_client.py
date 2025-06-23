
import httpx
from config.config import TELEGRAM_API
from config.config import API_KEY

async def send_update_success_message(user):
    async with httpx.AsyncClient() as client:
        try:
            url = f"{TELEGRAM_API}/client/update/success/{user.telegram_chat_id}"
            headers = {
                "X-API-Key": API_KEY,
                "Accept": "application/json"
            }
            response = await client.post(url=url, headers=headers)
            response.raise_for_status()  # Проверка на ошибки HTTP
            return response
        except httpx.HTTPStatusError as e:
            return e.response  # Возвращаем ответ с ошибкой для дальнейшей обработки
        except Exception as e:
            return httpx.Response(status_code=500, text=str(e))