import { ComponentFixture, TestBed } from '@angular/core/testing';

import { TaskSchemaComponent } from './task.component';

describe('TaskSchemaComponent', () => {
  let component: TaskSchemaComponent;
  let fixture: ComponentFixture<TaskSchemaComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [TaskSchemaComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(TaskSchemaComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
