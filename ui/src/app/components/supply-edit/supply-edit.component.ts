import { ChangeDetectorRef, Component, EventEmitter, Input, OnInit, Output } from '@angular/core';
import { FormArray, FormControl, FormGroup } from '@angular/forms';
import { MachineSchema, SupplySchema, createSupply, deleteSupply, getMachines, updateSupply } from 'src/client';

@Component({
  selector: 'app-supply-edit',
  templateUrl: './supply-edit.component.html',
  styleUrl: './supply-edit.component.css'
})
export class SupplyEditComponent implements OnInit {
  @Input() open: boolean = false;
  @Input() create: boolean = false;
  @Output() close = new EventEmitter();
  public deleting = false;
  @Input() public supply: SupplySchema
  public machines: MachineSchema[] = [];
  public units: string[] = ["each", "quart", "gallon"]
  public submitting: boolean = false;
  supplyForm = new FormGroup({
    name: new FormControl(''),
    machine_id: new FormControl(null),
    quantity_on_hand: new FormControl<number>(0),
    unit: new FormControl(''),
    parts: new FormArray([
    ])
  })
  constructor(private cdr: ChangeDetectorRef) {

  }
  async ngOnInit(): Promise<void> {
    if (!this.create && this.supply) {
      this.supplyForm.patchValue(this.supply)
      this.supply.parts.forEach((part) => {
        this.supplyForm.controls['parts'].push(new FormGroup({name: new FormControl(part.name), link: new FormControl(part.link)}))
      })
      console.log(this.supply);
      console.log(this.supplyForm)
      // this.cdr.detectChanges();
    } else {
      this.addEmptyPart()
    }
    this.machines = await getMachines()
  }

  public async deleteSupply() {
    this.deleting = true
    await deleteSupply({supplyId: this.supply.id});
    this.deleting = false
    this.supplyForm.reset()
    this.close.emit();
  }
  addEmptyPart() {
    this.supplyForm.controls['parts'].push(new FormGroup({name: new FormControl(''), link: new FormControl('')}))
  }
  deletePart(index: number) {
    this.supplyForm.controls.parts.removeAt(index);
  }
  async submit() {
    this.submitting = true;
    this.supply = this.supplyForm.getRawValue()
    if (this.supply.machine_id == 'null') {
      this.supply = null;
    }
    if (this.supply.id) {
      await updateSupply({supplyId: this.supply.id, requestBody: this.supply})
    } else {
      await createSupply({requestBody:this.supply})
    }
    this.supplyForm.reset()
    this.close.emit();
  }
}
