import { A2UIFrame, A2UIComponent } from "./types";

export interface SurfaceState {
  surfaceId: string;
  components: Map<string, A2UIComponent>;
  dataModel: Record<string, unknown>;
}

export type SurfaceListener = () => void;

export class A2UIStore {
  private surfaces = new Map<string, SurfaceState>();
  private listeners = new Set<SurfaceListener>();

  getSurfaces(): SurfaceState[] {
    return Array.from(this.surfaces.values());
  }

  getSurface(id: string): SurfaceState | undefined {
    return this.surfaces.get(id);
  }

  subscribe(listener: SurfaceListener): () => void {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  private notify() {
    for (const l of this.listeners) l();
  }

  applyFrame(frame: A2UIFrame) {
    if (frame.version !== "1.0" && frame.version !== "v1.0") {
      console.warn("[A2UI] version mismatch:", frame.version);
    }

    if (frame.createSurface) {
      const { surfaceId, components, dataModel } = frame.createSurface;
      const compMap = new Map<string, A2UIComponent>();
      for (const c of components) compMap.set(c.id, c);
      this.surfaces.set(surfaceId, {
        surfaceId,
        components: compMap,
        dataModel: dataModel ?? {},
      });
      this.notify();
      return;
    }

    if (frame.updateComponents) {
      const { surfaceId, components } = frame.updateComponents;
      const surface = this.surfaces.get(surfaceId);
      if (!surface) {
        console.warn("[A2UI] updateComponents for unknown surface:", surfaceId);
        return;
      }
      for (const c of components) surface.components.set(c.id, c);
      this.notify();
      return;
    }

    if (frame.updateDataModel) {
      const { surfaceId, path, value } = frame.updateDataModel;
      const surface = this.surfaces.get(surfaceId);
      if (!surface) {
        console.warn("[A2UI] updateDataModel for unknown surface:", surfaceId);
        return;
      }
      this.setByPath(surface.dataModel, path, value);
      this.notify();
      return;
    }

    if (frame.deleteSurface) {
      this.surfaces.delete(frame.deleteSurface.surfaceId);
      this.notify();
      return;
    }
  }

  private setByPath(obj: Record<string, unknown>, path: string, value: unknown) {
    const parts = path.split("/").filter(Boolean);
    let current: any = obj;
    for (let i = 0; i < parts.length - 1; i++) {
      const key = parts[i];
      if (current[key] === undefined || current[key] === null) {
        current[key] = {};
      }
      current = current[key];
    }
    current[parts[parts.length - 1]] = value;
  }
}
