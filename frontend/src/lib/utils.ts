// Utility functions for VeriCloud frontend
import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge";

/**
 * Combines class names with Tailwind CSS classes
 * Used by UI components for conditional styling
 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

/**
 * Formats a date string or Date object to a readable format
 * Used in the Reports page
 */
export function formatDate(date: Date | string): string {
  const d = typeof date === "string" ? new Date(date) : date;
  return d.toLocaleDateString("en-US", {
    year: "numeric",
    month: "long",
    day: "numeric",
  });
}