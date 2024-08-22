import { Component } from '@angular/core';
import { CreateTaskData, TasksByStateSchema, MachineSchema, SupplySchema, TaskCreateSchema, TaskSchema, TaskSupplySchema, createTask, getAllTasksByState, getMachines, getSupplies } from 'src/client';
import { SelectedSupply } from '../../models/selected-supply.model';

@Component({
  selector: 'app-tasks',
  templateUrl: './tasks.component.html',
  styleUrl: './tasks.component.css'
})
export class TasksComponent {
  public tasksByState: TasksByStateSchema;
  public tasks: TaskSchema[] = [];
  public machines: MachineSchema[] = [];
  public machinesById: Map<string, MachineSchema> = new Map();
  public task: TaskCreateSchema = {
    description: 'TaskSchema', time_interval: 0, meter_interval: 0,
    task_supplies: [],
    recurring: false,
    due_date: undefined,
    due_meter_reading: 0
  }
  public selectedMachineId: string;
  public showCreate: boolean = false;
  public loading = true;
  public supplies: SelectedSupply[] = [];
  public selectedSupply: SelectedSupply;
  public selectedSupplies: SelectedSupply[] = [];
  public allSupplies: SupplySchema[] = [];
  constructor() {
    this.selectedMachineId = ''
  }
  async ngOnInit(): Promise<void> {
    await this.fetchData()
    this.viewDueTasks();
    this.selectedMachineId = null;
  }
  public openCreate() {
    this.showCreate = true;
  }
  public async createTask() {
    this.task.task_supplies = this.selectedSupplies.map((ss) => {
      return {} as TaskSupplySchema
    })
    const taskDef = await createTask({ machineId: this.selectedMachineId, requestBody: this.task })

    // if (this.selectedSupplies && this.selectedSupplies.length > 0) {
    //   try {
    //     await assignSupplies({ machineId: this.selectedMachineSchemaId, taskDefId: taskDef.id, requestBody: this.selectedSupplies.map((s) => s.toTaskupplySchema(taskDef.id)) })
    //   } catch (error) {
    //     await deleteTaskSchema({ taskId: taskDef.id })
    //   }
    // }
    this.showCreate = false;
    this.viewDueTasks();
  }
  private sortTasks(tasks: TaskSchema[]) {
    return tasks.sort((a, b) => {
      if (a.completed && !b.completed) return 1;
      if (!a.completed && b.completed) return -1;
      if (a.due_meter_ago > 0 && b.due_meter_ago <= 0) return -1;
      if (b.due_meter_ago > 0 && a.due_meter_ago <= 0) return 1;
      if (a.due_days_ago > 0 && b.due_days_ago <= 0) return -1;
      if (b.due_days_ago > 0 && a.due_days_ago <= 0) return 1;
      // if (a.task.overdue_reason && !b.task.overdue_reason) return -1;
      // if (!a.task.overdue_reason && b.task.overdue_reason) return 1;
      if (a.due_days_ago < b.due_days_ago) return 1;
      if (a.due_days_ago > b.due_days_ago) return -1;
      if (a.due_meter_ago < b.due_meter_ago) return 1;
      if (a.due_meter_ago > b.due_meter_ago) return -1;
      return 0;
    });
  }
  public closeCreate() {
    this.showCreate = false;
  }
  public viewAllTasks() {
    this.tasks = this.sortTasks(this.tasksByState.completed.concat(this.tasksByState.due, this.tasksByState.upcoming))
  }
  public viewDueTasks() {
    this.tasks = this.sortTasks(this.tasksByState.due)
  }
  public viewUpcomingTasks() {
    this.tasks = this.sortTasks(this.tasksByState.upcoming)
  }
  private isDue(machine: MachineSchema, task: TaskSchema) {
    return task.completed == false && (task.due_meter_reading <= machine.current_meter_reading || new Date(task.due_date) <= new Date())
  }
  public updateInitialMeter() {
    this.task.due_meter_reading = this.machinesById.get(this.selectedMachineId).current_meter_reading
  }
  public reloadSupplies(): void {
    this.supplies = this.allSupplies.filter((s) => {
      return s.machine_id == this.selectedMachineId || s.machine_id == null
    }).map((s) => new SelectedSupply(s));
  }
  public async fetchData() {
    this.loading = true;
    this.tasksByState = await getAllTasksByState()
    console.log(this.tasksByState)
    this.machines = await getMachines()
    this.machinesById = this.machines.reduce((machines, machine) => {
      machines.set(machine.id, machine)
      return machines;
    }, new Map<string, MachineSchema>())
    this.allSupplies = await getSupplies()
    this.viewAllTasks()
    console.log(this.tasks);
    this.loading = false;
  }
}
