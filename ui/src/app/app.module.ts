import { CUSTOM_ELEMENTS_SCHEMA, NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { NavigationComponent } from './components/navigation/navigation.component'
import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { RouterModule, provideRouter } from '@angular/router';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ClarityModule, ClrFormsModule, ClrInput, ClrInputContainer } from '@clr/angular';
import { TaskComponent } from './components/task/task.component';
import { TasksComponent } from './components/tasks/tasks.component';
import { MachinesComponent } from './components/machines/machines.component';
import { UnitPluralPipe } from './pipes/unit-plural.pipe';
import { MachineComponent } from './components/machine/machine.component';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { CompletedTasksPipe } from './pipes/completed-tasks.pipe';
import { DueTasksPipe } from './pipes/due-tasks.pipe';
import { OverduePipe } from './pipes/overdue.pipe';
import { ReactiveFormsModule } from '@angular/forms';
import { TaskStatusBadgeComponent } from './components/task-status-badge/task-status-badge.component';
import '@cds/core/icon/register.js';
import { ClarityIcons, homeIcon, fuelIcon, tasksIcon, toolsIcon, plusIcon, plusCircleIcon, floppyIcon, trashIcon } from '@cds/core/icon';
import { SuppliesComponent } from './components/supplies/supplies.component';
import { MachineEditComponent } from './components/machine-edit/machine-edit.component';
import { ModalService } from './services/modal.service';
import { TaskSupplyStatusBadgeComponent } from './components/task-supply-status-badge/task-supply-status-badge.component';
import { SupplyEditComponent } from './components/supply-edit/supply-edit.component';
import '@cds/core/input/register.js';
import { CdsModule } from '@cds/angular';

ClarityIcons.addIcons(homeIcon, fuelIcon, tasksIcon, toolsIcon, plusCircleIcon, floppyIcon, trashIcon);
@NgModule({
  schemas: [CUSTOM_ELEMENTS_SCHEMA],
  declarations: [
    AppComponent,
    NavigationComponent,
    TaskComponent,
    TasksComponent,
    MachinesComponent, 
    UnitPluralPipe,
    MachineComponent,
    CompletedTasksPipe,
    DueTasksPipe,
    OverduePipe,
    TaskStatusBadgeComponent,
    SuppliesComponent,
    MachineEditComponent,
    TaskSupplyStatusBadgeComponent,
    SupplyEditComponent
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
