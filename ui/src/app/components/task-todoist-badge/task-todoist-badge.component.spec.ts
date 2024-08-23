import { ComponentFixture, TestBed } from '@angular/core/testing';

import { TaskTodoistBadgeComponent } from './task-todoist-badge.component';

describe('TaskTodoistBadgeComponent', () => {
  let component: TaskTodoistBadgeComponent;
  let fixture: ComponentFixture<TaskTodoistBadgeComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [TaskTodoistBadgeComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(TaskTodoistBadgeComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
