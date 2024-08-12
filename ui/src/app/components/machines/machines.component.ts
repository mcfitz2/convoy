import { NgFor } from '@angular/common';
import { Component, EventEmitter, OnInit, Output } from '@angular/core';
import { Machine, MachineCreate, MachineDetailed, createMachine, getMachines } from 'src/client';
import { FormControl, FormGroup, Validators } from '@angular/forms';

@Component({
  selector: 'app-machines',
  templateUrl: './machines.component.html',
  styleUrl: './machines.component.css'
})
export class MachinesComponent implements OnInit {
  public machines: MachineDetailed[] = [];
  public loading: boolean = true;
  public createMode: boolean = false;
  protected readonly form = new FormGroup({
    files: new FormControl<FileList | null>(null),
  });
  public machine: MachineCreate = {
    meter_unit: '',
    make: '',
    model: '',
    year: 0,
    image: '',
  }

  ngOnInit(): void {
    this.fetchData();
  }
  async fetchData() {
    console.log('fetching')
    this.loading = true;
    this.machines = await getMachines()
    this.loading = false;
  }
  public openCreate() {
    this.createMode = true;
  }
  public modalClosed() {
    this.createMode = false;
    this.fetchData()
  }  
  public onImagePicked(event: Event) {
    let reader = new FileReader();
    const target: HTMLInputElement = event.target as HTMLInputElement;
    if (target.files && target.files.length > 0) {
      const file = target.files.item(0)
      reader.readAsDataURL(file);

      reader.onload = () => {
        this.machine.image = reader.result.toString();
      };
    }
  }
}

