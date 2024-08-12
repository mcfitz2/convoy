import { Pipe, PipeTransform } from '@angular/core';
import { TaskDefinition, TaskDetailed } from 'src/client';
import { UnitPluralPipe } from './unit-plural.pipe';

@Pipe({
  name: 'overdue',
})
export class OverduePipe implements PipeTransform {

  transform(task: TaskDetailed, mode?: string): string {
    if (task) {
      if (mode == 'current') {
        if (task.overdue_reason == 'METER') {
          if (task.due_meter_ago > 0)
            return `Overdue by ${task.due_meter_ago} ${new UnitPluralPipe().transform(task.machine.meter_unit)}`
          if (task.due_meter_ago == 0)
            return `Due now`
          return 'Not Due'
        } else if (task.overdue_reason == 'TIME') {
          if (task.due_days_ago > 0)
            return `Overdue by ${task.due_days_ago} days`
          if (task.due_meter_ago == 0)
            return `Due now`
          return 'Not Due'
        } else if (task.overdue_reason == 'BOTH') {
          if (task.due_meter_ago > 0 && task.due_days_ago > 0)
            return `Overdue by ${task.due_meter_ago} ${new UnitPluralPipe().transform(task.machine.meter_unit)} and ${task.due_days_ago} days`
          if (task.due_meter_ago == 0 && task.due_days_ago == 0)
            return `Due now`
          return 'Not Due'
        } else {
          return 'Not Due'
        }
      } else if (mode == 'history') {
        if (task.overdue_reason == 'METER') {
          if (task.due_meter_ago > 0)
            return `Overdue by ${task.due_meter_ago} ${new UnitPluralPipe().transform(task.machine.meter_unit)}`
          if (task.due_meter_ago == 0)
            return `No`
          return 'Not Due -meter'
        } else if (task.overdue_reason == 'TIME') {
          if (task.due_days_ago > 0)
            return `Overdue by ${task.due_days_ago} days`
          if (task.due_meter_ago == 0)
            return `No`
          return 'Not Due - time'

        } else if (task.overdue_reason == 'BOTH') {
          if (task.due_meter_ago > 0 && task.due_days_ago > 0)
            return `Overdue by ${task.due_meter_ago} ${new UnitPluralPipe().transform(task.machine.meter_unit)} and ${task.due_days_ago} days`
          if (task.due_meter_ago == 0 && task.due_days_ago == 0)
            return `No`
          return JSON.stringify(task)
        } else {
          return 'No'
        }
      } else {
        return 'no mode'
      }
    } else {
      return 'Task is Falsy';
    }
  }

}
