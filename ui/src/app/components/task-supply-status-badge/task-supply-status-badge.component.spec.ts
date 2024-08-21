import { ComponentFixture, TestBed } from '@angular/core/testing';

import { TaskSchemaSupplySchemaStatusBadgeComponent } from './task-supply-status-badge.component';

describe('TaskSchemaSupplySchemaStatusBadgeComponent', () => {
  let component: TaskSchemaSupplySchemaStatusBadgeComponent;
  let fixture: ComponentFixture<TaskSchemaSupplySchemaStatusBadgeComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [TaskSchemaSupplySchemaStatusBadgeComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(TaskSchemaSupplySchemaStatusBadgeComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
