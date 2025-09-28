/**
 * Command Validator for Headless Chart Service
 * Ensures deterministic parsing and execution of chart commands
 */

interface ValidationResult {
  valid: boolean;
  normalizedCommands: string[];
  errors: string[];
  warnings: string[];
}

const VALID_COMMAND_PREFIXES = [
  'LOAD:',
  'TIMEFRAME:',
  'INDICATOR:',
  'DRAW:',
  'ANNOTATE:',
  'CLEAR:',
  'SUPPORT:',
  'RESISTANCE:',
  'FIBONACCI:',
  'TRENDLINE:',
  'ENTRY:',
  'TARGET:',
  'STOPLOSS:',
  'ZOOM:',
  'PAN:',
  'STYLE:',
  'ANALYZE:',
];

const VALID_TIMEFRAMES = ['1M', '5M', '15M', '30M', '1H', '4H', '1D', '1W', '1MON'];
const VALID_INDICATORS = ['MA20', 'MA50', 'MA200', 'BOLLINGER', 'RSI', 'MACD', 'VOLUME'];
const VALID_STYLES = ['CANDLES', 'LINE', 'AREA'];

export class CommandValidator {
  /**
   * Validate and normalize a list of chart commands
   */
  static validate(commands: string[]): ValidationResult {
    const result: ValidationResult = {
      valid: true,
      normalizedCommands: [],
      errors: [],
      warnings: [],
    };

    const commandSet = new Set<string>();
    const processedCommands: string[] = [];

    for (const command of commands) {
      // Trim and uppercase
      const normalizedCmd = command.trim().toUpperCase();
      
      if (!normalizedCmd) {
        result.warnings.push(`Empty command skipped`);
        continue;
      }

      // Check for valid prefix
      const hasValidPrefix = VALID_COMMAND_PREFIXES.some(prefix => 
        normalizedCmd.startsWith(prefix)
      );

      if (!hasValidPrefix) {
        result.errors.push(`Invalid command: ${command}`);
        result.valid = false;
        continue;
      }

      // Validate specific command types
      const validationError = this.validateSpecificCommand(normalizedCmd);
      if (validationError) {
        result.errors.push(validationError);
        result.valid = false;
        continue;
      }

      // Check for duplicates
      const commandKey = this.getCommandKey(normalizedCmd);
      if (commandSet.has(commandKey)) {
        result.warnings.push(`Duplicate command ignored: ${command}`);
        continue;
      }

      commandSet.add(commandKey);
      processedCommands.push(normalizedCmd);
    }

    // Apply command ordering rules
    result.normalizedCommands = this.orderCommands(processedCommands);

    // Add warnings for missing essential commands
    if (!result.normalizedCommands.some(cmd => cmd.startsWith('LOAD:'))) {
      result.warnings.push('No LOAD command found - chart may not display data');
    }

    return result;
  }

  /**
   * Validate specific command types
   */
  private static validateSpecificCommand(command: string): string | null {
    const [prefix, ...args] = command.split(':');
    
    switch (prefix) {
      case 'LOAD':
        if (args.length === 0 || args[0].length === 0) {
          return 'LOAD command requires a symbol';
        }
        if (args[0].length > 10) {
          return `Invalid symbol: ${args[0]}`;
        }
        break;

      case 'TIMEFRAME':
        if (args.length === 0 || !VALID_TIMEFRAMES.includes(args[0])) {
          return `Invalid timeframe: ${args[0]}. Valid: ${VALID_TIMEFRAMES.join(', ')}`;
        }
        break;

      case 'INDICATOR':
        if (args.length === 0 || !VALID_INDICATORS.includes(args[0])) {
          return `Invalid indicator: ${args[0]}. Valid: ${VALID_INDICATORS.join(', ')}`;
        }
        break;

      case 'STYLE':
        if (args.length === 0 || !VALID_STYLES.includes(args[0])) {
          return `Invalid style: ${args[0]}. Valid: ${VALID_STYLES.join(', ')}`;
        }
        break;

      case 'DRAW':
        if (args.length < 2) {
          return 'DRAW command requires type and parameters';
        }
        const drawType = args[0];
        if (!['LEVEL', 'TARGET', 'TRENDLINE'].includes(drawType)) {
          return `Invalid DRAW type: ${drawType}`;
        }
        break;

      case 'SUPPORT':
      case 'RESISTANCE':
      case 'ENTRY':
      case 'TARGET':
      case 'STOPLOSS':
        if (args.length === 0) {
          return `${prefix} command requires a price`;
        }
        const price = parseFloat(args[0]);
        if (isNaN(price) || price <= 0) {
          return `Invalid price for ${prefix}: ${args[0]}`;
        }
        break;

      case 'FIBONACCI':
        if (args.length < 2) {
          return 'FIBONACCI command requires high and low prices';
        }
        const high = parseFloat(args[0]);
        const low = parseFloat(args[1]);
        if (isNaN(high) || isNaN(low) || high <= low) {
          return `Invalid Fibonacci levels: high=${args[0]}, low=${args[1]}`;
        }
        break;

      case 'CLEAR':
        if (args.length === 0) {
          return 'CLEAR command requires a target (ALL, PATTERN, DRAWINGS)';
        }
        if (!['ALL', 'PATTERN', 'DRAWINGS'].some(t => args[0].startsWith(t))) {
          return `Invalid CLEAR target: ${args[0]}`;
        }
        break;
    }

    return null;
  }

  /**
   * Get a unique key for command deduplication
   */
  private static getCommandKey(command: string): string {
    const [prefix, ...args] = command.split(':');
    
    // For commands that should be unique
    if (['LOAD', 'TIMEFRAME', 'STYLE'].includes(prefix)) {
      return prefix;
    }
    
    // For indicators, allow multiple
    if (prefix === 'INDICATOR' && args.length > 0) {
      return `${prefix}:${args[0]}`;
    }
    
    // For drawing commands, use full command as key
    return command;
  }

  /**
   * Order commands for optimal execution
   */
  private static orderCommands(commands: string[]): string[] {
    const priority: { [key: string]: number } = {
      'CLEAR': 0,
      'LOAD': 1,
      'TIMEFRAME': 2,
      'STYLE': 3,
      'INDICATOR': 4,
      'SUPPORT': 5,
      'RESISTANCE': 5,
      'FIBONACCI': 6,
      'TRENDLINE': 7,
      'DRAW': 8,
      'ENTRY': 9,
      'TARGET': 9,
      'STOPLOSS': 9,
      'ANNOTATE': 10,
      'ZOOM': 11,
      'PAN': 12,
      'ANALYZE': 13,
    };

    return commands.sort((a, b) => {
      const prefixA = a.split(':')[0];
      const prefixB = b.split(':')[0];
      const priorityA = priority[prefixA] ?? 99;
      const priorityB = priority[prefixB] ?? 99;
      return priorityA - priorityB;
    });
  }

  /**
   * Create a command execution plan with timing
   */
  static createExecutionPlan(commands: string[]): Array<{ command: string; delay: number }> {
    const validated = this.validate(commands);
    if (!validated.valid) {
      throw new Error(`Invalid commands: ${validated.errors.join(', ')}`);
    }

    const plan: Array<{ command: string; delay: number }> = [];
    let cumulativeDelay = 0;

    for (const command of validated.normalizedCommands) {
      const [prefix] = command.split(':');
      
      // Determine delay based on command type
      let delay = 100; // Default delay
      
      switch (prefix) {
        case 'LOAD':
          delay = 500; // Loading data takes time
          break;
        case 'TIMEFRAME':
          delay = 300; // Changing timeframe needs settling
          break;
        case 'INDICATOR':
          delay = 200; // Adding indicators needs calculation
          break;
        case 'DRAW':
        case 'TRENDLINE':
        case 'FIBONACCI':
          delay = 150; // Drawing operations
          break;
        case 'CLEAR':
          delay = 200; // Clearing needs time
          break;
        case 'ANALYZE':
          delay = 1000; // Analysis takes longest
          break;
      }

      plan.push({ command, delay: cumulativeDelay });
      cumulativeDelay += delay;
    }

    return plan;
  }
}

export default CommandValidator;