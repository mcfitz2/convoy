import { Component, Input, OnInit } from '@angular/core';
import { MachineDetailed, TaskDetailed } from 'src/client';
import { UnitPluralPipe } from '../../pipes/unit-plural.pipe';

@Component({
  selector: 'app-task-supply-status-badge',
  templateUrl: './task-supply-status-badge.component.html',
  styleUrl: './task-supply-status-badge.component.css'
})
export class TaskSupplyStatusBadgeComponent implements OnInit {
  @Input() task: TaskDetailed
  public message = 'Not Implemented'
  public class: string;
  public ngOnInit() {
      const missing_supplies = this.task.task_definition.supplies.some((ts) => {
        return ts.supply.quantity_on_hand < ts.quantity
      })
      if (missing_supplies) {
        this.message = 'Missing Supplies'
        this.class = "label label-danger"
      } else {
        this.message = 'Supplies in Stock'
        this.class = "label label-success"
      }
  }
}
