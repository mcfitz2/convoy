import { Component, Input, OnInit } from '@angular/core';
import { MachineSchema, TaskSchema } from 'src/client';
import { UnitPluralPipe } from '../../pipes/unit-plural.pipe';

@Component({
  selector: 'app-task-status-badge',
  templateUrl: './task-status-badge.component.html',
  styleUrl: './task-status-badge.component.css'
})
export class TaskStatusBadgeComponent implements OnInit {
  @Input() machine: MachineSchema
  @Input() task: TaskSchema
  public message = 'Not Implemented'
  public class: string;
  public ngOnInit() {
    if (this.task.completed) {
      this.message = 'Completed'
      this.class = "label label-success"
      return
    } else if(this.task.due_days_ago > 0 && this.task.due_meter_ago > 0) {
      this.message = `Overdue by ${this.task.due_meter_ago} ${new UnitPluralPipe().transform(this.machine.meter_unit)} and ${this.task.due_days_ago} days`
      this.class = "label label-danger"
      return
    } else if(this.task.due_days_ago == 0 && this.task.due_meter_ago == 0) {
      this.message = `Due Now`
      this.class = "label label-danger"
      return
    } else if(this.task.due_days_ago < 0 && this.task.due_meter_ago < 0) {
      this.message = `Due in ${-1*this.task.due_meter_ago} ${new UnitPluralPipe().transform(this.machine.meter_unit)} or ${-1*this.task.due_days_ago} days`
      this.class = "label label-warning"
      return
    } else if(this.task.due_days_ago > 0) {
      this.message = `Overdue by ${this.task.due_days_ago} days`
      this.class = "label label-danger"
      return
    } else if(this.task.due_meter_ago > 0) {
      this.message = `Overdue by ${this.task.due_meter_ago} ${new UnitPluralPipe().transform(this.machine.meter_unit)}`
      this.class = "label label-danger"
      return
    } else if(this.task.due_meter_ago == 0 || this.task.due_days_ago == 0) {
      this.message = `Due Now`
      this.class = "label label-danger"
      return
    } else {
      this.message = 'Not Implemented'
      this.class = 'label'
      return
    }
  }
}
