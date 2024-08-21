import { Pipe, PipeTransform } from '@angular/core';
import { Task } from 'src/client';

@Pipe({
  name: 'dueTasks',
})
export class DueTasksPipe implements PipeTransform {
  private isDue(currentReading: number, task: Task) {
    return task.completed == false && (task.due_meter_reading <= currentReading || new Date(task.due_date) <= new Date())
  }
  transform(value: Task[], currentReading: number): number {
    return value.filter((task) => this.isDue(currentReading, task)).length;
  }

}
