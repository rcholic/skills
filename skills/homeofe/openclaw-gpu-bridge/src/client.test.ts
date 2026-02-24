import { GpuBridgeClient } from "./client";

describe("GpuBridgeClient multi-host", () => {
  afterEach(() => {
    jest.restoreAllMocks();
  });

  test("supports v0.1 fallback config via serviceUrl", async () => {
    const fetchMock = jest.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ status: "ok", device: "cuda" }),
    });
    global.fetch = fetchMock as unknown as typeof fetch;

    const client = new GpuBridgeClient({ serviceUrl: "http://legacy:8765" });
    const health = await client.health();

    expect(health.status).toBe("ok");
    expect(fetchMock.mock.calls.some((c) => c[0] === "http://legacy:8765/health")).toBe(true);
  });

  test("fails over to next host when first host is down", async () => {
    const fetchMock = jest.fn(async (url: string) => {
      if (url === "http://host-a:8765/health") {
        throw new Error("ECONNREFUSED");
      }
      if (url === "http://host-b:8765/health") {
        return { ok: true, json: async () => ({ status: "ok", device: "cuda" }) };
      }
      return { ok: true, json: async () => ({ status: "ok", device: "cuda" }) };
    });

    global.fetch = fetchMock as unknown as typeof fetch;

    const client = new GpuBridgeClient({
      hosts: [{ url: "http://host-a:8765" }, { url: "http://host-b:8765" }],
    });

    const health = await client.health();

    expect(health.status).toBe("ok");
    expect(fetchMock.mock.calls.some((c) => c[0] === "http://host-a:8765/health")).toBe(true);
    expect(fetchMock.mock.calls.some((c) => c[0] === "http://host-b:8765/health")).toBe(true);
  });

  test("least-busy selects host with lower VRAM utilization", async () => {
    const fetchMock = jest.fn(async (url: string) => {
      if (url === "http://host-a:8765/info") {
        return {
          ok: true,
          json: async () => ({ vram_total_mb: 1000, vram_used_mb: 900 }),
        };
      }

      if (url === "http://host-b:8765/info") {
        return {
          ok: true,
          json: async () => ({ vram_total_mb: 1000, vram_used_mb: 200 }),
        };
      }

      if (url === "http://host-b:8765/embed") {
        return {
          ok: true,
          json: async () => ({ embeddings: [[1, 2]], model: "all-MiniLM-L6-v2", dimensions: 2 }),
        };
      }

      return {
        ok: true,
        json: async () => ({ status: "ok", device: "cuda" }),
      };
    });

    global.fetch = fetchMock as unknown as typeof fetch;

    const client = new GpuBridgeClient({
      hosts: [{ url: "http://host-a:8765" }, { url: "http://host-b:8765" }],
      loadBalancing: "least-busy",
    });

    const result = await client.embed({ texts: ["hello"] });

    expect(result.dimensions).toBe(2);
    expect(fetchMock).toHaveBeenCalledWith("http://host-b:8765/embed", expect.any(Object));
  });
});
