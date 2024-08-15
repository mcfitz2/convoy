import { Pipe, PipeTransform } from '@angular/core';
import { TaskSchema } from 'src/client';

@Pipe({
  name: 'completedTasks',
})
export class CompletedTasksPipe implements PipeTransform {

  transform(value: TaskSchema[]): number {
    return value.filter((task) => task.completed).length;
  }

}
