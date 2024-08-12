import { Component, OnInit } from '@angular/core';
import { Supply, createSupply, getSupplies, updateSupply } from 'src/client';
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
  ngOnInit(): void {
    this.fetchData();
  }
  public supplies: ModifiableSupply[] = [];

  public addOne() {
    this.showCreate = true;
    this.createMode = true;
  }
  public fetchData() {
    getSupplies().then((supplies) => {
      this.supplies = supplies.map((s) => new ModifiableSupply(s));
    });
  }
  public saveSupply(supply: ModifiableSupply) {
    this.saving = true
    return supply.save().then(() => {
      this.saving = false
    })
  }
  public closeModal() {
    this.showCreate = false;
  }
}
