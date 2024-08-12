import { ComponentFixture, TestBed } from '@angular/core/testing';

import { TaskSupplyStatusBadgeComponent } from './task-supply-status-badge.component';

describe('TaskSupplyStatusBadgeComponent', () => {
  let component: TaskSupplyStatusBadgeComponent;
  let fixture: ComponentFixture<TaskSupplyStatusBadgeComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [TaskSupplyStatusBadgeComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(TaskSupplyStatusBadgeComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
