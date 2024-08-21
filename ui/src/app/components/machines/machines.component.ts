import { Component, OnInit } from '@angular/core';
import { FormControl, FormGroup } from '@angular/forms';
import { MachineSchema, getMachines } from 'src/client';

@Component({
  selector: 'app-machines',
  templateUrl: './machines.component.html',
  styleUrl: './machines.component.css'
})
export class MachinesComponent implements OnInit {
  public machines: MachineSchema[] = [];
  public loading: boolean = true;
  public createMode: boolean = false;
  protected readonly form = new FormGroup({
    files: new FormControl<FileList | null>(null),
  });
  public machine: MachineSchema = {
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

