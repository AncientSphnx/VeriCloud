/**
 * Utility functions for confidence level descriptions
 */

export interface ConfidenceResult {
  prediction: string;
  confidence: number;
  descriptiveLevel: string;
  description: string;
  colorClass: string;
}

/**
 * Get descriptive confidence level based on prediction and confidence score
 */
export function getConfidenceDescription(prediction: string, confidence: number): ConfidenceResult {
  const confidenceDecimal = confidence > 1 ? confidence / 100 : confidence;
  
  if (prediction.toLowerCase() === 'truthful') {
    if (confidenceDecimal >= 0.85) {
      return {
        prediction: 'Highly Truthful',
        confidence,
        descriptiveLevel: 'High Confidence',
        description: 'Strong indicators of truthfulness detected',
        colorClass: 'text-green-600'
      };
    } else if (confidenceDecimal >= 0.70) {
      return {
        prediction: 'Likely Truthful',
        confidence,
        descriptiveLevel: 'Medium-High Confidence',
        description: 'Moderate to strong truthfulness indicators',
        colorClass: 'text-green-500'
      };
    } else if (confidenceDecimal >= 0.55) {
      return {
        prediction: 'Possibly Truthful',
        confidence,
        descriptiveLevel: 'Low-Medium Confidence',
        description: 'Some truthfulness indicators, but not conclusive',
        colorClass: 'text-yellow-600'
      };
    } else {
      return {
        prediction: 'Uncertain - Leaning Truthful',
        confidence,
        descriptiveLevel: 'Low Confidence',
        description: 'Weak or ambiguous truthfulness indicators',
        colorClass: 'text-yellow-500'
      };
    }
  } else if (prediction.toLowerCase() === 'deceptive') {
    if (confidenceDecimal >= 0.85) {
      return {
        prediction: 'Highly Deceptive',
        confidence,
        descriptiveLevel: 'High Confidence',
        description: 'Strong indicators of deception detected',
        colorClass: 'text-red-600'
      };
    } else if (confidenceDecimal >= 0.70) {
      return {
        prediction: 'Likely Deceptive',
        confidence,
        descriptiveLevel: 'Medium-High Confidence',
        description: 'Moderate to strong deception indicators',
        colorClass: 'text-red-500'
      };
    } else if (confidenceDecimal >= 0.55) {
      return {
        prediction: 'Possibly Deceptive',
        confidence,
        descriptiveLevel: 'Low-Medium Confidence',
        description: 'Some deception indicators, but not conclusive',
        colorClass: 'text-orange-600'
      };
    } else {
      return {
        prediction: 'Uncertain - Leaning Deceptive',
        confidence,
        descriptiveLevel: 'Low Confidence',
        description: 'Weak or ambiguous deception indicators',
        colorClass: 'text-orange-500'
      };
    }
  }
  
  // Default case for unknown predictions
  return {
    prediction: 'Unknown',
    confidence,
    descriptiveLevel: 'Very Low Confidence',
    description: 'Unable to determine with confidence',
    colorClass: 'text-gray-500'
  };
}

/**
 * Get confidence color class for progress bars and indicators
 */
export function getConfidenceColor(confidence: number): string {
  const confidenceDecimal = confidence > 1 ? confidence / 100 : confidence;
  
  if (confidenceDecimal >= 0.85) return 'bg-green-500';
  if (confidenceDecimal >= 0.70) return 'bg-green-400';
  if (confidenceDecimal >= 0.55) return 'bg-yellow-500';
  if (confidenceDecimal >= 0.40) return 'bg-orange-500';
  return 'bg-red-500';
}

/**
 * Get confidence level badge variant for shadcn/ui
 */
export function getConfidenceBadgeVariant(confidence: number): 'default' | 'secondary' | 'destructive' | 'outline' {
  const confidenceDecimal = confidence > 1 ? confidence / 100 : confidence;
  
  if (confidenceDecimal >= 0.70) return 'default';
  if (confidenceDecimal >= 0.55) return 'secondary';
  return 'destructive';
}
