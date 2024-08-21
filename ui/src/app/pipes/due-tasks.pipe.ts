import { Pipe, PipeTransform } from '@angular/core';
import { TaskSchema } from 'src/client';

@Pipe({
  name: 'dueTasks',
})
export class DueTasksPipe implements PipeTransform {
  private isDue(currentReading: number, task: TaskSchema) {
    return task.completed == false && (task.due_meter_reading <= currentReading || new Date(task.due_date) <= new Date())
  }
  transform(value: TaskSchema[], currentReading: number): number {
    return value.filter((task) => this.isDue(currentReading, task)).length;
  }

}
