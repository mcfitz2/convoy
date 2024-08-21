import { Component, EventEmitter, Input, OnInit, Output } from '@angular/core';
import { Machine, Task, completeTask, deleteTask } from 'src/client';

@Component({
  selector: 'app-task',
  templateUrl: './task.component.html',
  styleUrl: './task.component.css'
})
export class TaskComponent implements OnInit {
  @Input() task!: Task;
  @Input() machine!: Machine;
  @Output() refresh = new EventEmitter();
  public showComplete: boolean = false;
  ngOnInit(): void {
    this.task.completed_meter_reading = this.machine.current_meter_reading
  }

  public openComplete() {
    this.showComplete = true;
  }
  
  public deleteTask() {
    deleteTask({machineId: this.machine.id, taskId: this.task.id}).then(() => {
      this.refresh.emit();
    })
  }
  public sendToTodoist() {
    
  }
  
  public cancel() {
    this.showComplete = false;
  }
  public completeTask() {
    const converted: Task = {
      id: this.task.id!, completed_date: this.task.completed_date!, completed_meter_reading: this.task.completed_meter_reading!,
      description: '',
      time_interval: 0,
      meter_interval: 0,
      supplies: []
    }
    completeTask({taskId: this.task.id!, machineId: this.machine.id, requestBody: converted}).then((task) => {
      this.showComplete = false;
      this.refresh.emit();
    })
  }
}
