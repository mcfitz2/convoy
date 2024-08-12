import { Component, EventEmitter, Input, OnInit, Output } from '@angular/core';
import { Machine, MachineCreate, MachineDetailed, createMachine, createReading, deleteMachine, updateMachine } from 'src/client';
import { ModalService } from '../../services/modal.service';
import { FormGroup, FormControl } from '@angular/forms';

@Component({
  selector: 'app-machine-edit',
  templateUrl: './machine-edit.component.html',
  styleUrl: './machine-edit.component.css'
})
export class MachineEditComponent implements OnInit {
  @Input() machine: MachineDetailed = {
    id: '',
    make: '',
    model: '',
    year: 0,
    meter_unit: '',
    meter_readings: [],
    task_definitions: [],
    tasks: [],
    current_meter_reading: 0,
    name: 0
  };
  @Input() open: boolean = false;
  @Input() create: boolean = false;
  public purchaseDate: Date;
  public historyMode: boolean = false;
  public maxYear: number = new Date().getFullYear() + 1
  @Output() close = new EventEmitter();
  machineForm = new FormGroup({
    year: new FormControl<number>(this.maxYear),
    make: new FormControl(''),
    meter_unit: new FormControl(''),
    model: new FormControl(''),
    image: new FormControl(null),
    purchase_date: new FormControl(null),
    meter_value: new FormControl<number>(0),
    file: new FormControl(null)
  })
  constructor() {

  }
  ngOnInit(): void {
    if (!this.create) {
      this.machineForm.patchValue(this.machine)
    }
  }
  public onImagePicked(event: Event) {
    let reader = new FileReader();
    const target: HTMLInputElement = event.target as HTMLInputElement;
    if (target.files && target.files.length > 0) {
      const file = target.files.item(0)
      reader.readAsDataURL(file);

      reader.onload = () => {
        this.machineForm.patchValue({ image: reader.result.toString() });
      };
    }
  }
  async deleteMachine() {
    await deleteMachine({machineId: this.machine.id})
    this.close.emit()
    this.machineForm.reset()
    this.machineForm.patchValue({file: null})
  }
  async submit() {
    try {
      if (this.create) {
        const newMachine: MachineCreate = this.machineForm.getRawValue();
        const createdMachine: Machine = await createMachine({ requestBody: newMachine })
        await createReading({ machineId: createdMachine.id, requestBody: { value: this.machineForm.get('meter_value').value } })
      } else {
        await updateMachine({ machineId: this.machine.id, requestBody: this.machine as MachineCreate })
        if (this.machine.current_meter_reading != this.machineForm.get('meter_value').value) {
          await createReading({ machineId: this.machine.id, requestBody: { value: this.machineForm.get('meter_value').value } })
        }
      }
    } catch(err) {
      console.error(err);
    }
    this.machineForm.reset()
    this.machineForm.patchValue({file: null})
    this.close.emit();
  }
}
