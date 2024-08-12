import { Component, EventEmitter, Input, OnInit, Output } from '@angular/core';
import { MachineDetailed, TaskComplete, TaskDetailed, completeTask, deleteTask, deleteTaskDefinition } from 'src/client';

@Component({
  selector: 'app-task',
  templateUrl: './task.component.html',
  styleUrl: './task.component.css'
})
export class TaskComponent implements OnInit {
  @Input() task!: TaskDetailed;
  @Input() machine!: MachineDetailed;
  @Output() refresh = new EventEmitter();
  public showComplete: boolean = false;
  ngOnInit(): void {
    this.task.completed_meter_reading = this.machine.current_meter_reading
  }

  public openComplete() {
    this.showComplete = true;
  }
  
  public deleteTask() {
    deleteTaskDefinition({taskId: this.task.task_definition.id}).then(() => {
      this.refresh.emit();
    })
  }
  public sendToTodoist() {
    
  }
  
  public cancel() {
    this.showComplete = false;
  }
  public completeTask() {
    const converted: TaskComplete = {id: this.task.id!, completed_date: this.task.completed_date!, completed_meter_reading: this.task.completed_meter_reading!}
    completeTask({taskId: this.task.id!, requestBody: converted}).then((task) => {
      this.showComplete = false;
      this.refresh.emit();
    })
  }
}
