import { ComponentFixture, TestBed } from '@angular/core/testing';

import { TaskSchemaStatusBadgeComponent } from './task-status-badge.component';

describe('TaskSchemaStatusBadgeComponent', () => {
  let component: TaskSchemaStatusBadgeComponent;
  let fixture: ComponentFixture<TaskSchemaStatusBadgeComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [TaskSchemaStatusBadgeComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(TaskSchemaStatusBadgeComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
