// frontend/src/components/FeatureFlagProvider.tsx

// The implementation of the FeatureFlagProvider is co-located with the context
// in `contexts/FeatureFlagContext.tsx` for simplicity and to avoid circular dependencies.
// This file is kept for structural clarity.

// You would wrap your application's root component with this provider.
// For example, in your main `App.tsx` or `main.tsx`:
/*
  import { FeatureFlagProvider } from './contexts/FeatureFlagContext';

  ReactDOM.createRoot(document.getElementById('root')!).render(
    <React.StrictMode>
      <FeatureFlagProvider>
        <App />
      </FeatureFlagProvider>
    </React.StrictMode>
  );
*/

// Re-exporting from the context file to make the import path cleaner.
export { FeatureFlagProvider } from '../contexts/FeatureFlagContext';
