import { Component, Input } from '@angular/core';
import { TaskSchema } from 'src/client';

@Component({
  selector: 'app-task-todoist-badge',
  templateUrl: './task-todoist-badge.component.html',
  styleUrl: './task-todoist-badge.component.css'
})
export class TaskTodoistBadgeComponent {
  @Input() task: TaskSchema;
  public class: string;
  public ngOnInit() {}
}
