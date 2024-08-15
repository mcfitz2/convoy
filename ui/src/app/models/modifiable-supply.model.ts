import { Signal } from "@angular/core"
import { SupplySchema, createSupply, deleteSupply, updateSupply } from "src/client"

export class ModifiableSupply {
    supply: SupplySchema
    modified: boolean = false
    blank: boolean = false
    constructor(supply: SupplySchema, blank: boolean = false) {
        this.supply = supply 
        this.blank = blank
    }
    public save(): Promise<SupplySchema> {
        if (this.supply.id) {
            return updateSupply({ supplyId: this.supply.id, requestBody: this.supply }).then((supply) => {
                this.modified = false
                this.blank = false;
                return supply
            })
        } else {
            return createSupply({ requestBody: this.supply }).then((supply) => {
                this.modified = false
                this.blank = false
                return supply
            })
        }
    }

    public delete(): Promise<SupplySchema> {
        return deleteSupply({supplyId: this.supply.id})
    }
}
