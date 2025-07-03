// frontend/src/utils/featureFlags.ts
import { FeatureFlags, defaultFlags } from '../config/featureFlags';

/**
 * Initializes the feature flags by merging defaults with environment variables
 * and localStorage overrides.
 *
 * The priority is:
 * 1. localStorage (for easy development overrides)
 * 2. Environment variables (for deployment-specific settings)
 * 3. Default configuration
 */
export const initializeFlags = (): FeatureFlags => {
  const flags: FeatureFlags = { ...defaultFlags };
  
  // 1. Apply environment variables
  // Vite exposes env vars via import.meta.env
  const backendFlagEnv = import.meta.env.VITE_APP_USE_BACKEND;
  if (backendFlagEnv) {
    flags.useBackendProcessing = backendFlagEnv.toLowerCase() === 'true';
  }

  // 2. Apply localStorage overrides
  try {
    const localFlagsJSON = localStorage.getItem('featureFlags');
    if (localFlagsJSON) {
      const localFlags = JSON.parse(localFlagsJSON);
      // Only apply valid keys from localStorage
      for (const key in defaultFlags) {
        if (Object.prototype.hasOwnProperty.call(localFlags, key)) {
          flags[key as keyof FeatureFlags] = localFlags[key];
        }
      }
    }
  } catch (error) {
    console.error("Failed to parse feature flags from localStorage:", error);
  }

  // Helper for developers in the console
  (window as any).setFeatureFlag = (flagName: keyof FeatureFlags, value: boolean) => {
    try {
        const localFlagsJSON = localStorage.getItem('featureFlags');
        const localFlags = localFlagsJSON ? JSON.parse(localFlagsJSON) : {};
        localFlags[flagName] = value;
        localStorage.setItem('featureFlags', JSON.stringify(localFlags));
        console.log(`Set ${flagName} to ${value}. Please refresh the page.`);
        window.location.reload();
    } catch (error) {
        console.error("Failed to set feature flag in localStorage:", error);
    }
  };


  return flags;
};
