import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SupplySchemaEditComponent } from './supply-edit.component';

describe('SupplySchemaEditComponent', () => {
  let component: SupplySchemaEditComponent;
  let fixture: ComponentFixture<SupplySchemaEditComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [SupplySchemaEditComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(SupplySchemaEditComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
