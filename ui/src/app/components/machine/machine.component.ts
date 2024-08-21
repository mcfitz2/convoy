import { Component, EventEmitter, Input, Output } from '@angular/core';
import { MachineSchema, TaskSchema } from 'src/client';

@Component({
  selector: 'app-machine',
  templateUrl: './machine.component.html',
  styleUrl: './machine.component.css'
})
export class MachineComponent {
  @Input() machine!: MachineSchema;
  public historyMode: boolean = false;
  public editMode: boolean = false;
  public maxYear: number = new Date().getFullYear() + 1
  @Output() refresh = new EventEmitter();
  constructor() {
  }
  public filterCompleted(tasks: TaskSchema[]) {
    return tasks.filter((t) => t.completed)
  }
  public modalClosed() {
    console.log("closingModal")
    this.editMode = false;
    this.refresh.emit()
  }
}
