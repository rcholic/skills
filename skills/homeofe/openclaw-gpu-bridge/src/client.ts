// GPU Bridge — HTTP Client with multi-host load balancing/failover

import type {
  GpuBridgeConfig,
  GpuHostConfig,
  HealthResponse,
  InfoResponse,
  BertScoreRequest,
  BertScoreResponse,
  EmbedRequest,
  EmbedResponse,
  LoadBalancingStrategy,
  StatusResponse,
} from "./types.js";

interface RuntimeHost {
  id: string;
  url: string;
  name: string;
  apiKey?: string;
  healthy: boolean;
  lastError?: string;
  lastInfo?: InfoResponse;
  lastCheckedAt?: number;
}

export class GpuBridgeClient {
  private hosts: RuntimeHost[];
  private timeout: number;
  private roundRobinIndex = 0;
  private strategy: LoadBalancingStrategy;
  private healthCheckIntervalMs: number;

  constructor(config: GpuBridgeConfig) {
    this.hosts = this.normalizeHosts(config);
    this.timeout = (config.timeout ?? 45) * 1000;
    this.strategy = config.loadBalancing ?? "round-robin";
    this.healthCheckIntervalMs = (config.healthCheckIntervalSeconds ?? 30) * 1000;

    const timer = setInterval(() => {
      void this.runHealthChecks();
    }, this.healthCheckIntervalMs);
    timer.unref?.();

    void this.runHealthChecks();
  }

  private normalizeHosts(config: GpuBridgeConfig): RuntimeHost[] {
    const hostsFromV2: GpuHostConfig[] = config.hosts ?? [];
    const v1Url = config.serviceUrl ?? config.url;

    const normalized: GpuHostConfig[] = hostsFromV2.length
      ? hostsFromV2
      : (v1Url ? [{ url: v1Url, apiKey: config.apiKey, name: "gpu-1" }] : []);

    if (!normalized.length) {
      throw new Error("GPU Bridge config invalid: set hosts[] (v0.2) or serviceUrl/url (v0.1)");
    }

    return normalized.map((host, i) => ({
      id: `host-${i + 1}`,
      url: host.url.replace(/\/+$/, ""),
      name: host.name ?? `gpu-${i + 1}`,
      apiKey: host.apiKey ?? config.apiKey,
      healthy: true,
    }));
  }

  private async requestFromHost<T>(host: RuntimeHost, path: string, options?: RequestInit): Promise<T> {
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
      ...(host.apiKey ? { "X-API-Key": host.apiKey } : {}),
    };

    const timeoutMs = path === "/health" ? 5000 : this.timeout;
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), timeoutMs);

    try {
      const res = await fetch(`${host.url}${path}`, {
        ...options,
        headers: { ...headers, ...(options?.headers as Record<string, string> | undefined) },
        signal: controller.signal,
      });

      if (!res.ok) {
        const body = await res.text().catch(() => "");
        throw new Error(`GPU host ${host.name} ${path} returned ${res.status}: ${body}`);
      }

      host.healthy = true;
      host.lastError = undefined;
      return (await res.json()) as T;
    } catch (error) {
      host.healthy = false;
      host.lastError = error instanceof Error ? error.message : String(error);
      throw error;
    } finally {
      clearTimeout(timer);
    }
  }

  private getHealthyHosts(): RuntimeHost[] {
    const healthy = this.hosts.filter((h) => h.healthy);
    return healthy.length ? healthy : this.hosts;
  }

  private async selectHost(path: string): Promise<RuntimeHost> {
    const pool = this.getHealthyHosts();

    if (this.strategy === "least-busy" && path !== "/health") {
      await Promise.all(pool.map(async (host) => {
        try {
          const info = await this.requestFromHost<InfoResponse>(host, "/info");
          host.lastInfo = info;
          host.lastCheckedAt = Date.now();
        } catch {
          // host health is already updated in requestFromHost
        }
      }));

      const candidates = this.getHealthyHosts();
      const byLeastBusy = [...candidates].sort((a, b) => this.vramLoad(a) - this.vramLoad(b));
      return byLeastBusy[0];
    }

    const host = pool[this.roundRobinIndex % pool.length];
    this.roundRobinIndex += 1;
    return host;
  }

  private vramLoad(host: RuntimeHost): number {
    const total = host.lastInfo?.vram_total_mb;
    const used = host.lastInfo?.vram_used_mb;
    if (!total || total <= 0 || used === undefined) {
      return Number.POSITIVE_INFINITY;
    }
    return used / total;
  }

  private async requestWithFailover<T>(path: string, options?: RequestInit): Promise<T> {
    const attempts = this.hosts.length;
    const tried = new Set<string>();
    let lastError: unknown;

    for (let i = 0; i < attempts; i += 1) {
      const host = await this.selectHost(path);
      if (tried.has(host.id)) {
        continue;
      }
      tried.add(host.id);

      try {
        return await this.requestFromHost<T>(host, path, options);
      } catch (error) {
        lastError = error;
      }
    }

    throw new Error(`All GPU hosts failed for ${path}: ${lastError instanceof Error ? lastError.message : String(lastError)}`);
  }

  private async runHealthChecks(): Promise<void> {
    await Promise.all(this.hosts.map(async (host) => {
      try {
        await this.requestFromHost<HealthResponse>(host, "/health");
      } catch {
        // already tracked as unhealthy
      }
    }));
  }

  async health(): Promise<HealthResponse> {
    return this.requestWithFailover<HealthResponse>("/health");
  }

  async info(): Promise<InfoResponse> {
    return this.requestWithFailover<InfoResponse>("/info");
  }

  async bertscore(req: BertScoreRequest): Promise<BertScoreResponse> {
    return this.requestWithFailover<BertScoreResponse>("/bertscore", {
      method: "POST",
      body: JSON.stringify(req),
    });
  }

  async embed(req: EmbedRequest): Promise<EmbedResponse> {
    return this.requestWithFailover<EmbedResponse>("/embed", {
      method: "POST",
      body: JSON.stringify(req),
    });
  }

  async status(): Promise<StatusResponse> {
    return this.requestWithFailover<StatusResponse>("/status");
  }
}
