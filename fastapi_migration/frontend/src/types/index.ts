export * from './dna';
export * from './analysis';
export * from './report';

// Notification types
export interface Notification {
  id: string;
  type: 'success' | 'error' | 'info' | 'warning';
  message: string;
  details?: string;
  duration?: number;
}