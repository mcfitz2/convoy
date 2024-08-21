import { Component, EventEmitter, Input, OnInit, Output } from '@angular/core';
import { ModifiableSupply } from 'src/app/models/modifiable-supply.model';

@Component({
  selector: 'app-supply',
  templateUrl: './supply.component.html',
  styleUrl: './supply.component.css'
})
export class SupplyComponent implements OnInit {
  @Input() public msupply: ModifiableSupply
  @Output() close = new EventEmitter();
  public showCreate: boolean = false;

  constructor() {
  }
  ngOnInit(): void {
  }

  public closeModal() {
    this.showCreate = false;
    this.close.emit();
  }
}
