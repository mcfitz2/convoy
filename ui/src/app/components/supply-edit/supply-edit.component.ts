import { Component, EventEmitter, Input, Output } from '@angular/core';
import { FormGroup, FormControl, FormArray } from '@angular/forms';
import { ModifiableSupply } from 'src/app/models/modifiable-supply.model';
import { MachineDetailed, SupplyDetailed, createSupply, getMachines } from 'src/client';

@Component({
  selector: 'app-supply-edit',
  templateUrl: './supply-edit.component.html',
  styleUrl: './supply-edit.component.css'
})
export class SupplyEditComponent {
  @Input() open: boolean = false;
  @Input() create: boolean = false;
  @Output() close = new EventEmitter();
  public deleting = false;
  public supply: SupplyDetailed
  public machines: MachineDetailed[] = [];
  public units: string[] = ["each", "quart", "gallon"]

  supplyForm = new FormGroup({
    name: new FormControl(''),
    machine_id: new FormControl(''),
    quantity_on_hand: new FormControl<number>(0),
    unit: new FormControl(''),
    parts: new FormArray([
    ])
  })
  constructor() {

  }
  async ngOnInit(): Promise<void> {
    if (!this.create) {
      this.supplyForm.patchValue(this.supply)
    }
    this.machines = await getMachines()
    console.log(this.machines)
    this.addEmptyPart()
  }
  public async deleteSupply() {
    this.deleting = true
    // await this.supply.delete().then(() => {
    //   this.deleting = false
    //   //this.supplies.splice(this.supplies.indexOf(supply), 1)
    // })
  }
  addEmptyPart() {
    this.supplyForm.controls['parts'].push(new FormGroup({name: new FormControl(''), link: new FormControl('')}))
  }
  deletePart(index: number) {
    this.supplyForm.controls.parts.removeAt(index);
  }
  async submit() {

    this.supply = this.supplyForm.getRawValue()
    console.log(this.supply)
    await createSupply({requestBody:this.supply})
    this.supplyForm.reset()
    this.close.emit();
  }
}
