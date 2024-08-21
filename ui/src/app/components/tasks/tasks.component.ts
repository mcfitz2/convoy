import { Component } from '@angular/core';
import { Machine, Task, createTask, getMachines, getSupplies, deleteTask, Supply, TaskCreate, TaskSupply } from 'src/client';
import { SelectedSupply } from '../../models/selected-supply.model';

@Component({
  selector: 'app-tasks',
  templateUrl: './tasks.component.html',
  styleUrl: './tasks.component.css'
})
export class TasksComponent {
  public tasks: { machine: Machine, task: Task}[] = [];
  public machines: Machine[] = [];
  public machinesById: Map<string, Machine> = new Map();
  public task: TaskCreate = {
    description: 'Task', time_interval: 0, meter_interval: 0,
    supplies: []
  }
  public selectedMachineId: string;
  public showCreate: boolean = false;
  public loading = true;
  public supplies: SelectedSupply[] = [];
  public selectedSupply: SelectedSupply;
  public selectedSupplies: SelectedSupply[] = [];
  private allSupplies: Supply[] = [];
  constructor() {
    this.selectedMachineId = ''
  }
  ngOnInit(): void {
    this.viewDueTasks();
    this.selectedMachineId = null;
  }
  public openCreate() {
    this.showCreate = true;
  }
  public async createTask() {
    this.task.supplies = this.selectedSupplies.map((ss) => {
      return {name: ss.name, unit: ss.unit, quantity_required: ss.quantity, parts: ss.supply.parts, supply_id: ss.supply_id} as TaskSupply
    })
    const taskDef = await createTask({ machineId: this.selectedMachineId, requestBody: this.task })

    // if (this.selectedSupplies && this.selectedSupplies.length > 0) {
    //   try {
    //     await assignSupplies({ machineId: this.selectedMachineId, taskDefId: taskDef.id, requestBody: this.selectedSupplies.map((s) => s.toTaskSupply(taskDef.id)) })
    //   } catch (error) {
    //     await deleteTask({ taskId: taskDef.id })
    //   }
    // }
    this.showCreate = false;
    this.viewDueTasks();
  }
  public closeCreate() {
    this.showCreate = false;
  }
  public viewAllTasks() {
    this.fetchData(true, true);
  }
  public viewDueTasks() {
    this.fetchData();
  }
  public viewUpcomingTasks() {
    this.fetchData(true)
  }
  private isDue(machine: Machine, task: Task) {
    return task.completed == false && (task.due_meter_reading <= machine.current_meter_reading || new Date(task.due_date) <= new Date())
  }
  public updateInitialMeter() {
    this.task.initial_due_meter = this.machinesById.get(this.selectedMachineId).current_meter_reading
  }
  public reloadSupplies(): void {
    this.supplies = this.allSupplies.filter((s) => {
      return s.machine_id == this.selectedMachineId || s.machine_id == null
    }).map((s) => new SelectedSupply(s));
  }
  public fetchData(includeNotDue: boolean = false, includeCompleted: boolean = false) {
    getMachines().then((machines: Machine[]) => {
      this.loading = false;
      const t: { machine: Machine, task: Task}[] = [];
      this.machines = machines;
      machines.forEach((machine) => {
        this.machinesById.set(machine.id, machine);
        if (includeNotDue) {
          
            machine.tasks.forEach((task) => {
              if (!task.completed || includeCompleted) {
                t.push({ machine: machine, task: task})
              }
            })
        } else {
            machine.tasks.forEach((task) => {
              if ((this.isDue(machine, task) && (!task.completed || includeCompleted))) {
                t.push({ machine: machine, task: task})
              }
            })

        }
      })
      this.tasks = t.sort((a, b) => {
        if (a.task.completed && !b.task.completed) return 1;
        if (!a.task.completed && b.task.completed) return -1;
        if (a.task.due_meter_ago > 0 && b.task.due_meter_ago <= 0) return -1;
        if (b.task.due_meter_ago > 0 && a.task.due_meter_ago <= 0) return 1;
        if (a.task.due_days_ago > 0 && b.task.due_days_ago <= 0) return -1;
        if (b.task.due_days_ago > 0 && a.task.due_days_ago <= 0) return 1;
        // if (a.task.overdue_reason && !b.task.overdue_reason) return -1;
        // if (!a.task.overdue_reason && b.task.overdue_reason) return 1;
        if (a.task.due_days_ago < b.task.due_days_ago) return 1;
        if (a.task.due_days_ago > b.task.due_days_ago) return -1;
        if (a.task.due_meter_ago < b.task.due_meter_ago) return 1;
        if (a.task.due_meter_ago > b.task.due_meter_ago) return -1;
        return 0;
      });
    }).then(getSupplies).then((supplies) => {
      this.allSupplies = supplies;
    });
  }
}
