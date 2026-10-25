declare namespace Entity {
  type PhoneOs = import("zod").infer<typeof import("@/schemas/phoneSchemas").phoneOsSchema>;

  type PhoneCondition = import("zod").infer<typeof import("@/schemas/phoneSchemas").phoneConditionSchema>;

  type Phone = import("zod").infer<typeof import("@/schemas/phoneSchemas").phoneSchema>;

  type PhoneDescription = import("zod").infer<typeof import("@/schemas/phoneSchemas").phoneDescriptionSchema>;

  type PhoneContact = import("zod").infer<typeof import("@/schemas/phoneSchemas").phoneContactSchema>;
}

declare namespace Api {
  interface CreatePhoneRequest extends Entity.PhoneDescription {
    condition: Entity.PhoneCondition;
    condition_note: string;
    price: number;
  }

  type MyListingsResponse = import("zod").infer<typeof import("@/schemas/phoneSchemas").myListingsResponseSchema>;
}
