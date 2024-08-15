// This file is auto-generated by @hey-api/openapi-ts

export const $APIResponse = {
    properties: {
        message: {
            type: 'string',
            title: 'Message'
        },
        status: {
            '$ref': '#/components/schemas/Status'
        }
    },
    type: 'object',
    required: ['message', 'status'],
    title: 'APIResponse'
} as const;

export const $AssignedTaskSupplySchema = {
    properties: {
        quantity: {
            type: 'number',
            title: 'Quantity',
            default: 0
        },
        supply_id: {
            type: 'string',
            title: 'Supply Id'
        }
    },
    type: 'object',
    required: ['supply_id'],
    title: 'AssignedTaskSupplySchema'
} as const;

export const $CompleteTaskSchema = {
    properties: {
        id: {
            type: 'string',
            title: 'Id'
        },
        completed: {
            type: 'boolean',
            title: 'Completed',
            default: true
        },
        completed_date: {
            type: 'string',
            format: 'date',
            title: 'Completed Date'
        },
        completed_meter_reading: {
            type: 'number',
            title: 'Completed Meter Reading'
        },
        notes: {
            anyOf: [
                {
                    type: 'string'
                },
                {
                    type: 'null'
                }
            ],
            title: 'Notes'
        }
    },
    type: 'object',
    required: ['id', 'completed_date', 'completed_meter_reading'],
    title: 'CompleteTaskSchema'
} as const;

export const $CreateMachineSchema = {
    properties: {
        make: {
            type: 'string',
            title: 'Make'
        },
        model: {
            type: 'string',
            title: 'Model'
        },
        year: {
            type: 'integer',
            title: 'Year'
        },
        image: {
            anyOf: [
                {
                    type: 'string'
                },
                {
                    type: 'null'
                }
            ],
            title: 'Image'
        },
        meter_unit: {
            type: 'string',
            title: 'Meter Unit'
        }
    },
    type: 'object',
    required: ['make', 'model', 'year', 'meter_unit'],
    title: 'CreateMachineSchema'
} as const;

export const $CreateTaskDefinitionSchema = {
    properties: {
        description: {
            type: 'string',
            title: 'Description'
        },
        time_interval: {
            type: 'integer',
            title: 'Time Interval'
        },
        meter_interval: {
            type: 'number',
            title: 'Meter Interval'
        },
        recurring: {
            anyOf: [
                {
                    type: 'boolean'
                },
                {
                    type: 'null'
                }
            ],
            title: 'Recurring',
            default: false
        },
        notes: {
            anyOf: [
                {
                    type: 'string'
                },
                {
                    type: 'null'
                }
            ],
            title: 'Notes'
        },
        machine_id: {
            anyOf: [
                {
                    type: 'string'
                },
                {
                    type: 'null'
                }
            ],
            title: 'Machine Id'
        },
        initial_due_meter: {
            anyOf: [
                {
                    type: 'number'
                },
                {
                    type: 'null'
                }
            ],
            title: 'Initial Due Meter'
        },
        initial_due_date: {
            anyOf: [
                {
                    type: 'string',
                    format: 'date'
                },
                {
                    type: 'null'
                }
            ],
            title: 'Initial Due Date'
        }
    },
    type: 'object',
    required: ['description', 'time_interval', 'meter_interval', 'machine_id'],
    title: 'CreateTaskDefinitionSchema'
} as const;

export const $HTTPValidationError = {
    properties: {
        detail: {
            items: {
                '$ref': '#/components/schemas/ValidationError'
            },
            type: 'array',
            title: 'Detail'
        }
    },
    type: 'object',
    title: 'HTTPValidationError'
} as const;

export const $Machine = {
    properties: {
        id: {
            type: 'string',
            title: 'Id'
        },
        meter_unit: {
            type: 'string',
            title: 'Meter Unit'
        },
        make: {
            type: 'string',
            title: 'Make'
        },
        model: {
            type: 'string',
            title: 'Model'
        },
        year: {
            type: 'integer',
            title: 'Year'
        },
        image: {
            type: 'string',
            title: 'Image'
        },
        purchase_date: {
            anyOf: [
                {
                    type: 'string',
                    format: 'date'
                },
                {
                    type: 'null'
                }
            ],
            title: 'Purchase Date'
        }
    },
    type: 'object',
    required: ['meter_unit', 'make', 'model', 'year', 'image'],
    title: 'Machine'
} as const;

export const $MachineSchema = {
    properties: {
        id: {
            type: 'string',
            title: 'Id'
        },
        make: {
            type: 'string',
            title: 'Make'
        },
        model: {
            type: 'string',
            title: 'Model'
        },
        year: {
            type: 'integer',
            title: 'Year'
        },
        image: {
            anyOf: [
                {
                    type: 'string'
                },
                {
                    type: 'null'
                }
            ],
            title: 'Image'
        },
        meter_unit: {
            type: 'string',
            title: 'Meter Unit'
        },
        meter_readings: {
            items: {
                '$ref': '#/components/schemas/MeterReading'
            },
            type: 'array',
            title: 'Meter Readings'
        },
        task_definitions: {
            items: {
                '$ref': '#/components/schemas/TaskDefinition'
            },
            type: 'array',
            title: 'Task Definitions'
        },
        tasks: {
            items: {
                '$ref': '#/components/schemas/TaskSchema'
            },
            type: 'array',
            title: 'Tasks'
        },
        current_meter_reading: {
            anyOf: [
                {
                    type: 'number'
                },
                {
                    type: 'null'
                }
            ],
            title: 'Current Meter Reading',
            readOnly: true
        },
        name: {
            type: 'integer',
            title: 'Name',
            readOnly: true
        }
    },
    type: 'object',
    required: ['id', 'make', 'model', 'year', 'meter_unit', 'meter_readings', 'task_definitions', 'tasks', 'current_meter_reading', 'name'],
    title: 'MachineSchema'
} as const;

export const $MeterReading = {
    properties: {
        id: {
            type: 'string',
            title: 'Id'
        },
        value: {
            type: 'number',
            title: 'Value'
        },
        timestamp: {
            type: 'string',
            format: 'date-time',
            title: 'Timestamp'
        },
        machine_id: {
            anyOf: [
                {
                    type: 'string'
                },
                {
                    type: 'null'
                }
            ],
            title: 'Machine Id'
        }
    },
    type: 'object',
    required: ['value'],
    title: 'MeterReading'
} as const;

export const $MeterReadingSchema = {
    properties: {
        id: {
            type: 'string',
            title: 'Id',
            primary_key: true
        },
        value: {
            type: 'number',
            title: 'Value'
        },
        timestamp: {
            type: 'string',
            format: 'date-time',
            title: 'Timestamp'
        },
        machine_id: {
            anyOf: [
                {
                    type: 'string'
                },
                {
                    type: 'null'
                }
            ],
            title: 'Machine Id'
        },
        machine: {
            '$ref': '#/components/schemas/Machine'
        }
    },
    type: 'object',
    required: ['value', 'machine_id', 'machine'],
    title: 'MeterReadingSchema'
} as const;

export const $Part = {
    properties: {
        id: {
            type: 'string',
            title: 'Id'
        },
        name: {
            type: 'string',
            title: 'Name'
        },
        link: {
            anyOf: [
                {
                    type: 'string'
                },
                {
                    type: 'null'
                }
            ],
            title: 'Link'
        },
        supply_id: {
            type: 'string',
            title: 'Supply Id'
        }
    },
    type: 'object',
    required: ['name'],
    title: 'Part'
} as const;

export const $Status = {
    type: 'string',
    enum: ['SUCCESS', 'ERROR'],
    title: 'Status'
} as const;

export const $Supply = {
    properties: {
        id: {
            type: 'string',
            title: 'Id'
        },
        name: {
            type: 'string',
            title: 'Name'
        },
        unit: {
            type: 'string',
            title: 'Unit'
        },
        quantity_on_hand: {
            type: 'number',
            title: 'Quantity On Hand',
            default: 0
        },
        machine_id: {
            anyOf: [
                {
                    type: 'string'
                },
                {
                    type: 'null'
                }
            ],
            title: 'Machine Id'
        }
    },
    type: 'object',
    required: ['name', 'unit'],
    title: 'Supply'
} as const;

export const $SupplySchema = {
    properties: {
        id: {
            type: 'string',
            title: 'Id',
            primary_key: true
        },
        name: {
            type: 'string',
            title: 'Name'
        },
        unit: {
            type: 'string',
            title: 'Unit'
        },
        quantity_on_hand: {
            type: 'number',
            title: 'Quantity On Hand',
            default: 0
        },
        parts: {
            items: {
                '$ref': '#/components/schemas/Part'
            },
            type: 'array',
            title: 'Parts',
            default: []
        },
        machine_id: {
            anyOf: [
                {
                    type: 'string'
                },
                {
                    type: 'null'
                }
            ],
            title: 'Machine Id'
        }
    },
    type: 'object',
    required: ['name', 'unit', 'machine_id'],
    title: 'SupplySchema'
} as const;

export const $TaskDefinition = {
    properties: {
        id: {
            type: 'string',
            title: 'Id'
        },
        description: {
            type: 'string',
            title: 'Description'
        },
        time_interval: {
            type: 'integer',
            title: 'Time Interval'
        },
        meter_interval: {
            type: 'number',
            title: 'Meter Interval'
        },
        recurring: {
            anyOf: [
                {
                    type: 'boolean'
                },
                {
                    type: 'null'
                }
            ],
            title: 'Recurring',
            default: false
        },
        notes: {
            anyOf: [
                {
                    type: 'string'
                },
                {
                    type: 'null'
                }
            ],
            title: 'Notes'
        },
        machine_id: {
            anyOf: [
                {
                    type: 'string'
                },
                {
                    type: 'null'
                }
            ],
            title: 'Machine Id'
        }
    },
    type: 'object',
    required: ['description', 'time_interval', 'meter_interval'],
    title: 'TaskDefinition'
} as const;

export const $TaskDefinitionSchema = {
    properties: {
        id: {
            type: 'string',
            title: 'Id'
        },
        description: {
            type: 'string',
            title: 'Description'
        },
        time_interval: {
            type: 'integer',
            title: 'Time Interval'
        },
        meter_interval: {
            type: 'number',
            title: 'Meter Interval'
        },
        recurring: {
            anyOf: [
                {
                    type: 'boolean'
                },
                {
                    type: 'null'
                }
            ],
            title: 'Recurring',
            default: false
        },
        notes: {
            anyOf: [
                {
                    type: 'string'
                },
                {
                    type: 'null'
                }
            ],
            title: 'Notes'
        },
        machine_id: {
            anyOf: [
                {
                    type: 'string'
                },
                {
                    type: 'null'
                }
            ],
            title: 'Machine Id'
        },
        supplies: {
            items: {
                '$ref': '#/components/schemas/TaskSupplySchema'
            },
            type: 'array',
            title: 'Supplies'
        }
    },
    type: 'object',
    required: ['id', 'description', 'time_interval', 'meter_interval', 'machine_id', 'supplies'],
    title: 'TaskDefinitionSchema'
} as const;

export const $TaskSchema = {
    properties: {
        id: {
            type: 'string',
            title: 'Id',
            primary_key: true
        },
        completed: {
            type: 'boolean',
            title: 'Completed',
            default: false
        },
        completed_date: {
            anyOf: [
                {
                    type: 'string',
                    format: 'date'
                },
                {
                    type: 'null'
                }
            ],
            title: 'Completed Date'
        },
        completed_meter_reading: {
            anyOf: [
                {
                    type: 'number'
                },
                {
                    type: 'null'
                }
            ],
            title: 'Completed Meter Reading'
        },
        due_date: {
            type: 'string',
            format: 'date',
            title: 'Due Date'
        },
        due_meter_reading: {
            type: 'number',
            title: 'Due Meter Reading'
        },
        notes: {
            anyOf: [
                {
                    type: 'string'
                },
                {
                    type: 'null'
                }
            ],
            title: 'Notes'
        },
        task_definition_id: {
            anyOf: [
                {
                    type: 'string'
                },
                {
                    type: 'null'
                }
            ],
            title: 'Task Definition Id'
        },
        task_definition: {
            anyOf: [
                {
                    '$ref': '#/components/schemas/TaskDefinitionSchema'
                },
                {
                    type: 'null'
                }
            ]
        },
        machine_id: {
            anyOf: [
                {
                    type: 'string'
                },
                {
                    type: 'null'
                }
            ],
            title: 'Machine Id'
        },
        machine: {
            '$ref': '#/components/schemas/Machine'
        },
        due_meter_ago: {
            type: 'number',
            title: 'Due Meter Ago',
            readOnly: true
        },
        due_days_ago: {
            type: 'number',
            title: 'Due Days Ago',
            readOnly: true
        },
        overdue_reason: {
            type: 'string',
            title: 'Overdue Reason',
            readOnly: true
        }
    },
    type: 'object',
    required: ['due_date', 'task_definition_id', 'task_definition', 'machine_id', 'machine', 'due_meter_ago', 'due_days_ago', 'overdue_reason'],
    title: 'TaskSchema'
} as const;

export const $TaskSupplySchema = {
    properties: {
        quantity: {
            type: 'number',
            title: 'Quantity',
            default: 0
        },
        supply_id: {
            type: 'string',
            title: 'Supply Id'
        },
        supply: {
            '$ref': '#/components/schemas/Supply'
        }
    },
    type: 'object',
    required: ['supply_id', 'supply'],
    title: 'TaskSupplySchema'
} as const;

export const $ValidationError = {
    properties: {
        loc: {
            items: {
                anyOf: [
                    {
                        type: 'string'
                    },
                    {
                        type: 'integer'
                    }
                ]
            },
            type: 'array',
            title: 'Location'
        },
        msg: {
            type: 'string',
            title: 'Message'
        },
        type: {
            type: 'string',
            title: 'Error Type'
        }
    },
    type: 'object',
    required: ['loc', 'msg', 'type'],
    title: 'ValidationError'
} as const;