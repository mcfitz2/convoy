import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SupplySchemaComponent } from './supply.component';

describe('SupplySchemaComponent', () => {
  let component: SupplySchemaComponent;
  let fixture: ComponentFixture<SupplySchemaComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [SupplySchemaComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(SupplySchemaComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
