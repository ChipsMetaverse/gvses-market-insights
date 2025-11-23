/**
 * Widget Parser Utility
 * Detects and parses ChatKit widget JSON from Agent Builder responses
 */

export type WidgetType =
  | 'Card'
  | 'ListView'
  | 'ListViewItem'
  | 'Title'
  | 'Divider'
  | 'Text'
  | 'Caption'
  | 'Badge'
  | 'Image'
  | 'Row'
  | 'Col'
  | 'Spacer'
  | 'Button'
  | 'Box';

export interface WidgetDefinition {
  type: WidgetType;
  value?: string | number;
  label?: string;
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl' | '2xl' | '3xl' | 'full';
  weight?: 'normal' | 'medium' | 'semibold' | 'bold';
  spacing?: number;
  limit?: number;
  status?: {
    text: string;
    icon?: string;
  };
  src?: string;
  alt?: string;
  aspectRatio?: string;
  radius?: 'sm' | 'md' | 'lg' | 'xl' | 'full';
  frame?: boolean;
  color?: string;
  textColor?: string;
  background?: string;
  gap?: number;
  align?: 'start' | 'center' | 'end' | 'stretch' | 'baseline' | 'between' | 'evenly' | 'around';
  justify?: 'start' | 'center' | 'end' | 'between' | 'around' | 'evenly';
  wrap?: boolean;
  flex?: number;
  maxLines?: number;
  iconStart?: string;
  pill?: boolean;
  variant?: 'solid' | 'outline' | 'ghost' | 'soft';
  onClickAction?: {
    type: string;
    payload?: Record<string, unknown>;
  };
  children?: WidgetDefinition[];
  [key: string]: any;
}

export interface WidgetResponse {
  response_text?: string;
  query_intent?: string;
  symbol?: string;
  widgets?: WidgetDefinition[];
  text?: string;
  message?: string;
}

export interface ParsedResponse {
  hasWidgets: boolean;
  parsedResponse?: WidgetResponse;
  displayText?: string;
}

/**
 * Parse agent response to detect and extract widget JSON
 * @param text - Raw agent response text
 * @returns Parsed response with widget data if available
 */
export const parseAgentResponse = (text: string): ParsedResponse => {
  if (!text || typeof text !== 'string') {
    return {
      hasWidgets: false,
      displayText: text || ''
    };
  }

  try {
    // Try to parse as JSON
    const parsed: WidgetResponse = JSON.parse(text);

    // Check if response contains widgets array
    if (parsed.widgets && Array.isArray(parsed.widgets) && parsed.widgets.length > 0) {
      return {
        hasWidgets: true,
        parsedResponse: parsed,
        displayText: parsed.response_text || parsed.text || parsed.message || ''
      };
    }

    // JSON but no widgets - extract text if available
    if (parsed.text || parsed.message || parsed.response_text) {
      return {
        hasWidgets: false,
        displayText: parsed.text || parsed.message || parsed.response_text || text
      };
    }
  } catch {
    // Not JSON or invalid JSON - treat as plain text
  }

  return {
    hasWidgets: false,
    displayText: text
  };
};

/**
 * Validate widget structure
 * @param widget - Widget definition to validate
 * @returns true if widget has required properties
 */
export const isValidWidget = (widget: any): widget is WidgetDefinition => {
  return (
    widget &&
    typeof widget === 'object' &&
    typeof widget.type === 'string' &&
    [
      'Card',
      'ListView',
      'ListViewItem',
      'Title',
      'Divider',
      'Text',
      'Caption',
      'Badge',
      'Image',
      'Row',
      'Col',
      'Spacer',
      'Button',
      'Box',
    ].includes(widget.type)
  );
};

/**
 * Filter and validate widgets array
 * @param widgets - Array of widget definitions
 * @returns Validated widgets array
 */
export const validateWidgets = (widgets: any[]): WidgetDefinition[] => {
  if (!Array.isArray(widgets)) {
    return [];
  }

  return widgets.filter(isValidWidget);
};
