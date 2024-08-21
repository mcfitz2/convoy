import { Signal } from "@angular/core"
import { Supply, createSupply, deleteSupply, updateSupply } from "src/client"

export class ModifiableSupply {
    supply: Supply
    modified: boolean = false
    blank: boolean = false
    constructor(supply: Supply, blank: boolean = false) {
        this.supply = supply 
        this.blank = blank
    }
    public save(): Promise<Supply> {
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

    public delete(): Promise<Supply> {
        return deleteSupply({supplyId: this.supply.id})
    }
}
