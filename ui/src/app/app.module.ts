import { CommonModule } from '@angular/common';
import { CUSTOM_ELEMENTS_SCHEMA, NgModule } from '@angular/core';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { BrowserModule } from '@angular/platform-browser';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { CdsModule } from '@cds/angular';
import { ClarityIcons, floppyIcon, fuelIcon, homeIcon, plusCircleIcon, tasksIcon, toolsIcon, trashIcon } from '@cds/core/icon';
import '@cds/core/icon/register.js';
import '@cds/core/input/register.js';
import { ClarityModule, ClrFormsModule } from '@clr/angular';
import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { MachineEditComponent } from './components/machine-edit/machine-edit.component';
import { MachineComponent } from './components/machine/machine.component';
import { MachinesComponent } from './components/machines/machines.component';
import { NavigationComponent } from './components/navigation/navigation.component';
import { SuppliesComponent } from './components/supplies/supplies.component';
import { SupplyComponent } from './components/supply/supply.component';
import { CompletedTasksPipe } from './pipes/completed-tasks.pipe';
import { DueTasksPipe } from './pipes/due-tasks.pipe';
import { UnitPluralPipe } from './pipes/unit-plural.pipe';
import { ModalService } from './services/modal.service';
import { TasksComponent } from './components/tasks/tasks.component';
import { SupplyEditComponent } from './components/supply-edit/supply-edit.component';
import { TaskStatusBadgeComponent } from './components/task-status-badge/task-status-badge.component';
import { TaskSupplyStatusBadgeComponent } from './components/task-supply-status-badge/task-supply-status-badge.component';
import { TaskComponent } from './components/task/task.component';

ClarityIcons.addIcons(homeIcon, fuelIcon, tasksIcon, toolsIcon, plusCircleIcon, floppyIcon, trashIcon);
@NgModule({
  schemas: [CUSTOM_ELEMENTS_SCHEMA],
  declarations: [
    AppComponent,
    NavigationComponent,
    AppComponent,
    TasksComponent,
    MachineComponent, 
    UnitPluralPipe,
    MachinesComponent,
    CompletedTasksPipe,
    DueTasksPipe,
    SuppliesComponent,
    MachineEditComponent,
    TaskStatusBadgeComponent,
    SupplyComponent,
    SuppliesComponent,
    SupplyEditComponent,
    TaskSupplyStatusBadgeComponent,
    TaskComponent
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    BrowserAnimationsModule,
    CommonModule,
    ClarityModule,
    ClrFormsModule,
    FormsModule,
    ReactiveFormsModule,
    CdsModule

  ],
  providers: [ModalService],
  bootstrap: [AppComponent]
})
export class AppModule { }
