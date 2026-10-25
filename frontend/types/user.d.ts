declare namespace Entity {
  type User = import("zod").infer<typeof import("@/schemas/userSchemas").userSchema>;
}

declare namespace Api {
  interface CreateUserRequest {
    whatsapp: string;
    first_name: string;
    last_name: string;
  }

  type UpdateUserRequest = CreateUserRequest;
}
