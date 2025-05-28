import time
import asyncio
from app.celery.celery_app import celery_app
from app.services.tsp import solve_tsp
from app.schemas.graph import Graph, PathResult


def send_notification_sync(user_id: int, notification: dict):
    try:
        from app.websocket.manager import manager
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(manager.send_notification(user_id, notification))
        loop.close()
    except Exception as e:
        print(f"Error sending notification: {e}")


@celery_app.task(bind=True)
def solve_tsp_task(self, graph_data: dict, user_id: int):
    task_id = self.request.id
    
    try:
        send_notification_sync(user_id, {
            "status": "STARTED",
            "task_id": task_id,
            "message": "Task started"
        })
        
        graph = Graph(**graph_data)
        
        total_steps = 10
        for step in range(total_steps):
            progress = int((step + 1) / total_steps * 100)
            
            self.update_state(
                state='PROGRESS',
                meta={'progress': progress}
            )
            
            send_notification_sync(user_id, {
                "status": "PROGRESS",
                "task_id": task_id,
                "progress": progress
            })
            
            time.sleep(0.5)
        
        result = solve_tsp(graph)
        
        send_notification_sync(user_id, {
            "status": "COMPLETED",
            "task_id": task_id,
            "path": result.path,
            "total_distance": result.total_distance
        })
        
        return {
            "path": result.path,
            "total_distance": result.total_distance
        }
        
    except Exception as exc:
        send_notification_sync(user_id, {
            "status": "FAILED",
            "task_id": task_id,
            "message": f"Task execution error: {str(exc)}"
        })
        raise exc