export enum LogLevel {
  ERROR = 'error',
  WARN = 'warn',
  INFO = 'info',
  DEBUG = 'debug',
  TRACE = 'trace',
}

type LogData = Record<string, any>;

export class Logger {
  private static instance: Logger;
  private logLevel: LogLevel;
  private context: string;

  private constructor(context: string = 'ai-agent', logLevel: LogLevel = LogLevel.INFO) {
    this.context = context;
    this.logLevel = this.determineLogLevel(logLevel);
  }

  public static getLogger(context: string = 'ai-agent', logLevel?: LogLevel): Logger {
    if (!Logger.instance) {
      Logger.instance = new Logger(context, logLevel);
    }
    return Logger.instance;
  }

  public setLogLevel(level: LogLevel): void {
    this.logLevel = this.determineLogLevel(level);
  }

  public error(message: string, data?: LogData): void {
    this.log(LogLevel.ERROR, message, data);
  }

  public warn(message: string, data?: LogData): void {
    this.log(LogLevel.WARN, message, data);
  }

  public info(message: string, data?: LogData): void {
    this.log(LogLevel.INFO, message, data);
  }

  public debug(message: string, data?: LogData): void {
    this.log(LogLevel.DEBUG, message, data);
  }

  public trace(message: string, data?: LogData): void {
    this.log(LogLevel.TRACE, message, data);
  }

  private log(level: LogLevel, message: string, data: LogData = {}): void {
    if (this.shouldLog(level)) {
      const timestamp = new Date().toISOString();
      const logEntry = {
        timestamp,
        level: level.toUpperCase(),
        context: this.context,
        message,
        ...data,
      };

      const logString = JSON.stringify(logEntry, this.getCircularReplacer());
      
      switch (level) {
        case LogLevel.ERROR:
          console.error(logString);
          break;
        case LogLevel.WARN:
          console.warn(logString);
          break;
        case LogLevel.INFO:
          console.info(logString);
          break;
        case LogLevel.DEBUG:
        case LogLevel.TRACE:
          console.debug(logString);
          break;
      }
    }
  }

  private shouldLog(level: LogLevel): boolean {
    const levels = Object.values(LogLevel);
    const currentLevelIndex = levels.indexOf(this.logLevel);
    const messageLevelIndex = levels.indexOf(level);
    return messageLevelIndex <= currentLevelIndex;
  }

  private determineLogLevel(level?: LogLevel): LogLevel {
    if (level) return level;
    
    // Default to INFO in production, DEBUG in development
    return process.env.NODE_ENV === 'production' ? LogLevel.INFO : LogLevel.DEBUG;
  }

  private getCircularReplacer() {
    const seen = new WeakSet();
    return (key: string, value: any) => {
      if (typeof value === 'object' && value !== null) {
        if (seen.has(value)) {
          return '[Circular]';
        }
        seen.add(value);
      }
      return value;
    };
  }
}

// Convenience function for quick logging
export const log = {
  error: (message: string, data?: LogData) => Logger.getLogger().error(message, data),
  warn: (message: string, data?: LogData) => Logger.getLogger().warn(message, data),
  info: (message: string, data?: LogData) => Logger.getLogger().info(message, data),
  debug: (message: string, data?: LogData) => Logger.getLogger().debug(message, data),
  trace: (message: string, data?: LogData) => Logger.getLogger().trace(message, data),
};
