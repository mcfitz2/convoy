import { Component, EventEmitter, Input, Output } from '@angular/core';
import { FormControl, FormGroup } from '@angular/forms';
import { ModalService } from 'src/app/services/modal.service';
import { Machine, Task, createReading } from 'src/client';

@Component({
  selector: 'app-machine',
  templateUrl: './machine.component.html',
  styleUrl: './machine.component.css'
})
export class MachineComponent {
  @Input() machine!: Machine;
  public historyMode: boolean = false;
  public editMode: boolean = false;
  public maxYear: number = new Date().getFullYear() + 1
  @Output() refresh = new EventEmitter();
  constructor() {
  }
  public filterCompleted(tasks: Task[]) {
    return tasks.filter((t) => t.completed)
  }
  public modalClosed() {
    console.log("closingModal")
    this.editMode = false;
    this.refresh.emit()
  }
}
