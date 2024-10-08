import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { HomeComponent } from './components/home/home.component';
import { MachinesComponent } from './components/machines/machines.component';
import { SuppliesComponent } from './components/supplies/supplies.component';
import { TasksComponent } from './components/tasks/tasks.component';

const routes: Routes = [
  {path: 'machines', component: MachinesComponent},
  {path: 'tasks', component: TasksComponent},
  {path: 'home', component: HomeComponent},
  {path: 'supplies', component: SuppliesComponent},
  {path: '*', component: TasksComponent},
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
