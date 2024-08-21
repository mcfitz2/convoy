import { Component, EventEmitter, Input, OnInit, Output } from '@angular/core';
import { MachineSchema, TaskCompleteSchema, TaskSchema, completeTask, deleteTask } from 'src/client';

@Component({
  selector: 'app-task',
  templateUrl: './task.component.html',
  styleUrl: './task.component.css'
})
export class TaskComponent implements OnInit {
  @Input() task!: TaskSchema;
  @Input() machine!: MachineSchema;
  @Output() refresh = new EventEmitter();
  public showComplete: boolean = false;
  ngOnInit(): void {
    this.task.completed_meter_reading = this.machine.current_meter_reading
  }

  public openComplete() {
    this.showComplete = true;
  }

  public deleteTask() {
    deleteTask({ machineId: this.machine.id, taskId: this.task.id }).then(() => {
      this.refresh.emit();
    })
  }

  public cancel() {
    this.showComplete = false;
  }
  public completeTask() {
    const converted: TaskCompleteSchema = {
      completed_date: this.task.completed_date!, completed_meter_reading: this.task.completed_meter_reading!,
      notes: '',
    }
    completeTask({ taskId: this.task.id!, machineId: this.machine.id, requestBody: converted }).then(() => {
      this.showComplete = false;
      this.refresh.emit();
    })
  }
}
