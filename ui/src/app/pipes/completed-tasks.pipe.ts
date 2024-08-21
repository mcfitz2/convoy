import { Pipe, PipeTransform } from '@angular/core';
import { Task } from 'src/client';

@Pipe({
  name: 'completedTasks',
})
export class CompletedTasksPipe implements PipeTransform {

  transform(value: Task[]): number {
    return value.filter((task) => task.completed).length;
  }

}
