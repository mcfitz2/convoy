import { ComponentFixture, TestBed } from '@angular/core/testing';

import { MachineSchemaEditComponent } from './machine-edit.component';

describe('MachineSchemaEditComponent', () => {
  let component: MachineSchemaEditComponent;
  let fixture: ComponentFixture<MachineSchemaEditComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [MachineSchemaEditComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(MachineSchemaEditComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
