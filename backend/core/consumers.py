import json
from channels.generic.websocket import AsyncWebsocketConsumer

class AttendanceConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = 'attendance_updates'
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()
        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'message': 'Connected to VeriFace Real-Time Attendance WebSocket'
        }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            action = data.get('action')
            if action == 'subscribe_student':
                student_id = data.get('student_id')
                if student_id:
                    self.student_group = f"student_{student_id}"
                    await self.channel_layer.group_add(
                        self.student_group,
                        self.channel_name
                    )
                    await self.send(text_data=json.dumps({
                        'type': 'subscribed',
                        'student_id': student_id,
                        'message': f'Subscribed to live attendance alerts for student #{student_id}'
                    }))
        except Exception:
            pass

    async def scan_progress(self, event):
        """Dispatches live photo-by-photo AI progress (e.g. Photo 2/4 scanned)"""
        await self.send(text_data=json.dumps({
            'type': 'scan_progress',
            'current': event.get('current'),
            'total': event.get('total'),
            'percentage': event.get('percentage'),
            'faces_detected': event.get('faces_detected'),
            'message': event.get('message')
        }))

    async def attendance_confirmed(self, event):
        """Broadcasts confirmed attendance to students and teachers live"""
        await self.send(text_data=json.dumps({
            'type': 'attendance_confirmed',
            'class_id': event.get('class_id'),
            'subject_name': event.get('subject_name'),
            'subject_code': event.get('subject_code'),
            'teacher_name': event.get('teacher_name'),
            'date': event.get('date'),
            'records': event.get('records', [])
        }))
