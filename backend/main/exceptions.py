from fastapi import HTTPException


class MachineNotFound(HTTPException):
    def __init__(self, machine_id):
        super(MachineNotFound, self).__init__(status_code=404, detail=f"Could not find machine with ID={machine_id}")

class TaskNotFound(HTTPException):
    def __init__(self, machine_id, task_id):
        super(TaskNotFound, self).__init__(status_code=404, detail=f"Could not find task with ID={task_id}")