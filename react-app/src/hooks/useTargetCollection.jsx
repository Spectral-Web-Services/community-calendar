import React, { createContext, useContext, useState, useCallback } from 'react';
import { useCollections } from './useCollections.js';

const Ctx = createContext({ target: null, setTarget: () => {}, addToTarget: () => {} });

export function TargetCollectionProvider({ children }) {
  const { collections, addEventToCollection, createCollection, refresh } = useCollections();
  const [targetId, setTargetId] = useState(null);

  // Resolve target from collections (null if deleted or not found)
  const manualCollections = collections.filter(c => c.type !== 'auto');
  const target = targetId ? manualCollections.find(c => c.id === targetId) || null : null;

  const setTarget = useCallback((id) => setTargetId(id), []);

  const addToTarget = useCallback(async (eventId) => {
    if (!target) return;
    await addEventToCollection(target.id, eventId);
  }, [target, addEventToCollection]);

  return (
    <Ctx.Provider value={{ target, setTarget, addToTarget, manualCollections, createCollection, refresh }}>
      {children}
    </Ctx.Provider>
  );
}

export function useTargetCollection() {
  return useContext(Ctx);
}
