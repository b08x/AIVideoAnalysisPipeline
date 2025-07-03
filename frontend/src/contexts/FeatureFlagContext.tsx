// frontend/src/contexts/FeatureFlagContext.tsx
import React, { createContext, useContext, ReactNode } from 'react';
import { FeatureFlags, defaultFlags } from '../config/featureFlags';
import { initializeFlags } from '../utils/featureFlags';

// Create a context with the default flags as the initial value.
const FeatureFlagContext = createContext<FeatureFlags>(defaultFlags);

/**
 * The provider component that makes feature flag values available to its children.
 * It initializes the flags on mount.
 */
export const FeatureFlagProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const flags = initializeFlags();

  return (
    <FeatureFlagContext.Provider value={flags}>
      {children}
    </FeatureFlagContext.Provider>
  );
};

/**
 * Custom hook for components to easily access feature flag values.
 *
 * @example
 * const { useBackendProcessing } = useFeatureFlag();
 * if (useBackendProcessing) {
 * // ... render backend-specific UI
 * }
 */
export const useFeatureFlag = (): FeatureFlags => {
  return useContext(FeatureFlagContext);
};
