"use client";

import React, { createContext, useContext, useState, useCallback, useRef } from "react";
import { A2UIStore, SurfaceState } from "./store";
import { A2UIFrame } from "./types";

interface A2UIContextValue {
  surfaces: SurfaceState[];
  applyFrame: (frame: A2UIFrame) => void;
  clear: () => void;
}

const A2UIContext = createContext<A2UIContextValue>({
  surfaces: [],
  applyFrame: () => {},
  clear: () => {},
});

export function useA2UI() {
  return useContext(A2UIContext);
}

export function A2UIProvider({ children }: { children: React.ReactNode }) {
  const storeRef = useRef(new A2UIStore());
  const [surfaces, setSurfaces] = useState<SurfaceState[]>([]);

  React.useEffect(() => {
    return storeRef.current.subscribe(() => {
      setSurfaces(storeRef.current.getSurfaces());
    });
  }, []);

  const applyFrame = useCallback((frame: A2UIFrame) => {
    storeRef.current.applyFrame(frame);
  }, []);

  const clear = useCallback(() => {
    storeRef.current = new A2UIStore();
    setSurfaces([]);
  }, []);

  return (
    <A2UIContext.Provider value={{ surfaces, applyFrame, clear }}>
      {children}
    </A2UIContext.Provider>
  );
}
