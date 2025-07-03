// frontend/src/config/featureFlags.ts

/**
 * Defines the available feature flags in the application.
 * The key is the flag name, and the value is its default state.
 */
export interface FeatureFlags {
  useBackendProcessing: boolean;
  enableAdvancedVisualAnalysis: boolean;
  showProcessingETA: boolean;
}

export const defaultFlags: FeatureFlags = {
  /**
   * If true, the application will use the new Docker backend for all processing.
   * If false, it will fall back to the original client-side Gemini processing.
   */
  useBackendProcessing: false,
  /**
   * If true, enables more detailed (and potentially more expensive)
   * visual analysis models on the backend.
   */
  enableAdvancedVisualAnalysis: false,
  /**
   * If true, the UI will display an estimated time of arrival for job completion.
   */
  showProcessingETA: true,
};
