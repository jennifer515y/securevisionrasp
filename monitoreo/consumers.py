import json
from channels.generic.websocket import AsyncWebsocketConsumer

class EmployeeLocationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.employee_id = self.scope['url_route']['kwargs']['empleado_id']
        self.group_name = f"employee_{self.employee_id}"

        # Unirse al grupo
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        # Salir del grupo
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def send_location(self, event):
        # Enviar los datos al cliente WebSocket
        await self.send(text_data=json.dumps(event['data']))
