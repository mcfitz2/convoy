import { Pipe, PipeTransform } from '@angular/core';
import { TaskDetailed } from 'src/client';

@Pipe({
  name: 'completedTasks',
})
export class CompletedTasksPipe implements PipeTransform {

  transform(value: TaskDetailed[]): number {
    return value.filter((task) => task.completed).length;
  }

}
