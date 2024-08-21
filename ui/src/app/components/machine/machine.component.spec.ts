import { ComponentFixture, TestBed } from '@angular/core/testing';

import { MachineSchemaComponent } from './machine.component';

describe('MachineSchemaComponent', () => {
  let component: MachineSchemaComponent;
  let fixture: ComponentFixture<MachineSchemaComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [MachineSchemaComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(MachineSchemaComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
