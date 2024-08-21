import { ComponentFixture, TestBed } from '@angular/core/testing';

import { MachineSchemasComponent } from './machines.component';

describe('MachineSchemasComponent', () => {
  let component: MachineSchemasComponent;
  let fixture: ComponentFixture<MachineSchemasComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [MachineSchemasComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(MachineSchemasComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
