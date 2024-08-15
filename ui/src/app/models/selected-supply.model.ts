import { AssignedTaskSupplySchema, SupplySchema, TaskSupplySchema } from "src/client";

export class SelectedSupply {
    name: string;
    unit: string;
    quantity?: number;
    task_definition_id?: string | null;
    supply_id?: string | null;
    supply: SupplySchema;
    constructor(supply: SupplySchema) {
        this.name = supply.name;
        this.unit = supply.unit;
        this.quantity = 0;
        this.task_definition_id = null;
        this.supply_id = supply.id;
        this.supply = supply;
    }
    public toTaskSupply(taskDefId: string = null): AssignedTaskSupplySchema {
        return {
            quantity: this.quantity,
            task_definition_id: taskDefId || this.task_definition_id,
            supply_id: this.supply_id,
        } as AssignedTaskSupplySchema
    }
}
