import { afterEach, describe, expect, it, vi } from "vitest";
import { UserService } from "@/services/UserService";
import { jsonResponse } from "@/mocks/jsonResponse";
import { testUser } from "@/mocks/testUser";

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("UserService", () => {
  it("creates a user", async () => {
    const fetchMock = vi.fn<typeof fetch>(async () => jsonResponse(testUser, 201));
    vi.stubGlobal("fetch", fetchMock);
    const body = { whatsapp: testUser.whatsapp, first_name: testUser.first_name, last_name: testUser.last_name };

    expect(await UserService.create(body)).toEqual({ success: true, data: testUser, errorText: "" });
    expect(fetchMock.mock.calls[0]?.[0]).toBe("/api/users");
    expect(JSON.parse(String(fetchMock.mock.calls[0]?.[1]?.body))).toEqual(body);
  });

  it("loads a user by id", async () => {
    const fetchMock = vi.fn<typeof fetch>(async () => jsonResponse(testUser));
    vi.stubGlobal("fetch", fetchMock);

    expect(await UserService.getById(testUser.id)).toMatchObject({ success: true, data: testUser });
    expect(fetchMock.mock.calls[0]?.[0]).toBe(`/api/users/${testUser.id}`);
  });

  it("replaces the user data with PUT", async () => {
    const updatedUser = { ...testUser, whatsapp: "+14155550000" };
    const fetchMock = vi.fn<typeof fetch>(async () => jsonResponse(updatedUser));
    vi.stubGlobal("fetch", fetchMock);
    const body = { whatsapp: updatedUser.whatsapp, first_name: testUser.first_name, last_name: testUser.last_name };

    expect(await UserService.update(testUser.id, body)).toMatchObject({ success: true, data: updatedUser });
    expect(fetchMock.mock.calls[0]?.[0]).toBe(`/api/users/${testUser.id}`);
    expect(fetchMock.mock.calls[0]?.[1]?.method).toBe("PUT");
    expect(JSON.parse(String(fetchMock.mock.calls[0]?.[1]?.body))).toEqual(body);
  });
});
