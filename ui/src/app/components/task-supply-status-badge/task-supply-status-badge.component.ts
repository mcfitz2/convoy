import { Component, Input, OnInit } from '@angular/core';
import { Machine, Supply, Task, getSupplies } from 'src/client';
import { UnitPluralPipe } from '../../pipes/unit-plural.pipe';

@Component({
  selector: 'app-task-supply-status-badge',
  templateUrl: './task-supply-status-badge.component.html',
  styleUrl: './task-supply-status-badge.component.css'
})
export class TaskSupplyStatusBadgeComponent implements OnInit {
  @Input() task: Task
  public message: string = 'Not Implemented'
  public class: string = "label label-danger"
  suppliesById: Map<string, Supply> = new Map();
  public async ngOnInit() {
      this.suppliesById = (await getSupplies()).reduce((byId, supply) => {
        byId.set(supply.id, supply);
        return byId;
      }, new Map())
      const missing_supplies = this.task.supplies.some((ts) => {
        return this.suppliesById.get(ts.supply_id).quantity_on_hand < ts.quantity_required
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
