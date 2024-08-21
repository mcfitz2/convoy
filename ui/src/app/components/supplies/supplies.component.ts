import { Component, OnInit } from '@angular/core';
import { createSupply, getSupplies, updateSupply } from 'src/client';
import { ModifiableSupply } from '../../models/modifiable-supply.model';

@Component({
  selector: 'app-supplies',
  templateUrl: './supplies.component.html',
  styleUrl: './supplies.component.css'
})
export class SuppliesComponent implements OnInit {
  public saving = false;
  public deleting = false;
  public units: string[] = ["each", "quart", "gallon"]
  public showCreate = false;
  public createMode = false;
  async ngOnInit(): Promise<void> {
    await this.fetchData();
  }
  public supplies: ModifiableSupply[] = [];

  public addOne() {
    this.showCreate = true;
    this.createMode = true;
  }
  public async fetchData() {
    const supplies = await getSupplies();
    this.supplies = supplies.map((s) => new ModifiableSupply(s));
  }
  public async closeModal() {
    this.showCreate = false;
    await this.fetchData()
  }
}
