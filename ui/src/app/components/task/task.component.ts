import { Component, EventEmitter, Input, OnInit, Output } from '@angular/core';
import { MachineSchema, SupplySchema, TaskCompleteSchema, TaskSchema, completeTask, deleteTask, getMachine, syncToTodoist } from 'src/client';

@Component({
  selector: 'app-task',
  templateUrl: './task.component.html',
  styleUrl: './task.component.css'
})
export class TaskComponent implements OnInit {
  @Input() task!: TaskSchema;
  @Input() public supplies: SupplySchema[] = [];
  @Input() public machine!: MachineSchema;
  @Output() refresh = new EventEmitter();
  public showComplete: boolean = false;
  async ngOnInit(): Promise<void> {
    this.task.completed_meter_reading = this.machine.current_meter_reading
  }

  public openComplete() {
    this.showComplete = true;
  }

  public deleteTask() {
    deleteTask({ machineId: this.task.machine_id, taskId: this.task.id }).then(() => {
      this.refresh.emit();
    })
  }
  public async syncToTodoist() {
    await syncToTodoist({machineId: this.task.machine_id, taskId: this.task.id})
  }
  public cancel() {
    this.showComplete = false;
  }
  public completeTask() {
    const converted: TaskCompleteSchema = {
      completed_date: this.task.completed_date!, completed_meter_reading: this.task.completed_meter_reading!,
      notes: '',
    }
    completeTask({ taskId: this.task.id!, machineId: this.task.machine_id, requestBody: converted }).then(() => {
      this.showComplete = false;
      this.refresh.emit();
    })
  }
}
