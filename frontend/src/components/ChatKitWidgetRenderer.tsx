/**
 * ChatKit Widget Renderer
 * Renders ChatKit widgets from Agent Builder responses as visual components
 */

import React from 'react';
import type { LucideIcon } from 'lucide-react';
import { RefreshCcw, ExternalLink, Calendar, LineChart, Newspaper } from 'lucide-react';
import { WidgetDefinition } from '../utils/widgetParser';

type WidgetAction = WidgetDefinition['onClickAction'];

type WidgetActionHandler = (action: WidgetAction | undefined) => void;

const GAP_MULTIPLIER = 4; // Tailwind gap approximation (px)

const alignToCss = (align?: WidgetDefinition['align']): React.CSSProperties['alignItems'] => {
  switch (align) {
    case 'start':
      return 'flex-start';
    case 'center':
      return 'center';
    case 'end':
      return 'flex-end';
    case 'stretch':
      return 'stretch';
    case 'baseline':
      return 'baseline';
    case 'between':
    case 'around':
    case 'evenly':
      return 'center';
    default:
      return undefined;
  }
};

const justifyToCss = (justify?: WidgetDefinition['justify']): React.CSSProperties['justifyContent'] => {
  switch (justify) {
    case 'start':
      return 'flex-start';
    case 'center':
      return 'center';
    case 'end':
      return 'flex-end';
    case 'between':
      return 'space-between';
    case 'around':
      return 'space-around';
    case 'evenly':
      return 'space-evenly';
    default:
      return undefined;
  }
};

const textSizeClasses: Record<string, string> = {
  xs: 'text-xs',
  sm: 'text-sm',
  md: 'text-base',
  lg: 'text-lg',
  xl: 'text-xl',
  '2xl': 'text-2xl',
  '3xl': 'text-3xl',
};

const textColorClasses: Record<string, string> = {
  primary: 'text-blue-400',
  secondary: 'text-gray-400',
  success: 'text-green-400',
  danger: 'text-red-400',
  warning: 'text-yellow-400',
  info: 'text-sky-400',
};

const badgeColorClasses: Record<string, string> = {
  success: 'bg-green-500/10 text-green-400 border-green-500/20',
  danger: 'bg-red-500/10 text-red-400 border-red-500/20',
  warning: 'bg-yellow-500/10 text-yellow-300 border-yellow-500/30',
  info: 'bg-sky-500/10 text-sky-300 border-sky-500/20',
  neutral: 'bg-gray-500/10 text-gray-300 border-gray-500/20',
};

const buttonVariantClasses = (
  variant: WidgetDefinition['variant'],
  color?: string,
  size: WidgetDefinition['size'] = 'sm',
  pill = false,
): string => {
  const base = 'inline-flex items-center justify-center font-medium transition-colors focus:outline-none focus:ring-1 focus:ring-offset-1 disabled:opacity-60 disabled:pointer-events-none';

  const sizeClasses: Record<string, string> = {
    xs: 'h-7 px-2 text-xs',
    sm: 'h-8 px-3 text-xs',
    md: 'h-9 px-4 text-sm',
    lg: 'h-10 px-5 text-sm',
  };

  const shapeClass = pill ? 'rounded-full' : 'rounded-md';
  const colorKey = color?.toLowerCase() ?? 'neutral';

  const solidColors: Record<string, string> = {
    success: 'bg-green-500 text-white hover:bg-green-600',
    danger: 'bg-red-500 text-white hover:bg-red-600',
    warning: 'bg-yellow-500 text-black hover:bg-yellow-400',
    info: 'bg-sky-500 text-white hover:bg-sky-600',
    neutral: 'bg-slate-700 text-white hover:bg-slate-600',
  };

  const outlineColors: Record<string, string> = {
    success: 'border border-green-400 text-green-400 hover:bg-green-500/10',
    danger: 'border border-red-400 text-red-400 hover:bg-red-500/10',
    warning: 'border border-yellow-400 text-yellow-300 hover:bg-yellow-500/10',
    info: 'border border-sky-400 text-sky-300 hover:bg-sky-500/10',
    neutral: 'border border-slate-500 text-slate-200 hover:bg-slate-600/30',
  };

  const ghostColors: Record<string, string> = {
    success: 'text-green-400 hover:bg-green-500/10',
    danger: 'text-red-400 hover:bg-red-500/10',
    warning: 'text-yellow-300 hover:bg-yellow-500/10',
    info: 'text-sky-300 hover:bg-sky-500/10',
    neutral: 'text-slate-200 hover:bg-slate-600/40',
  };

  const variantClass = (() => {
    switch (variant) {
      case 'solid':
        return solidColors[colorKey] ?? solidColors.neutral;
      case 'outline':
        return outlineColors[colorKey] ?? outlineColors.neutral;
      case 'ghost':
        return ghostColors[colorKey] ?? ghostColors.neutral;
      case 'soft':
        return badgeColorClasses[colorKey] ?? badgeColorClasses.neutral;
      default:
        return solidColors.neutral;
    }
  })();

  return [base, shapeClass, sizeClasses[size ?? 'sm'] ?? sizeClasses.sm, variantClass].filter(Boolean).join(' ');
};

const radiusClasses: Record<string, string> = {
  sm: 'rounded-sm',
  md: 'rounded-md',
  lg: 'rounded-lg',
  xl: 'rounded-xl',
  full: 'rounded-full',
};

const iconRegistry: Record<string, LucideIcon> = {
  chart: LineChart,
  'chart-line': LineChart,
  calendar: Calendar,
  'refresh-ccw': RefreshCcw,
  refresh: RefreshCcw,
  'external-link': ExternalLink,
  newspaper: Newspaper,
};

interface ChatKitWidgetRendererProps {
  widgets: WidgetDefinition[];
  onAction?: WidgetActionHandler;
}

export const ChatKitWidgetRenderer: React.FC<ChatKitWidgetRendererProps> = ({ widgets, onAction }) => {
  if (!widgets || widgets.length === 0) {
    return null;
  }

  const handleAction: WidgetActionHandler = (action) => {
    if (!action) {
      return;
    }

    if (onAction) {
      onAction(action);
      return;
    }

    if (action.type === 'browser.openUrl' && typeof window !== 'undefined') {
      const url = (action.payload as { url?: string } | undefined)?.url;
      if (url) {
        window.open(url, '_blank', 'noopener,noreferrer');
        return;
      }
    }

    console.debug('[ChatKitWidgetRenderer] Triggered action:', action);
  };

  return (
    <div className="chatkit-widgets-container space-y-3">
      {widgets.map((widget, index) => (
        <WidgetComponent key={`${widget.type}-${index}`} definition={widget} onAction={handleAction} />
      ))}
    </div>
  );
};

const WidgetComponent: React.FC<{ definition: WidgetDefinition; onAction: WidgetActionHandler }> = ({ definition, onAction }) => {
  switch (definition.type) {
    case 'Card':
      return <CardWidget definition={definition} onAction={onAction} />;
    case 'ListView':
      return <ListViewWidget definition={definition} onAction={onAction} />;
    case 'ListViewItem':
      return <ListViewItemWidget definition={definition} onAction={onAction} />;
    case 'Title':
      return <TitleWidget definition={definition} />;
    case 'Divider':
      return <DividerWidget definition={definition} />;
    case 'Text':
      return <TextWidget definition={definition} />;
    case 'Caption':
      return <CaptionWidget definition={definition} />;
    case 'Badge':
      return <BadgeWidget definition={definition} />;
    case 'Image':
      return <ImageWidget definition={definition} />;
    case 'Row':
      return <RowWidget definition={definition} onAction={onAction} />;
    case 'Col':
      return <ColWidget definition={definition} onAction={onAction} />;
    case 'Spacer':
      return <SpacerWidget definition={definition} />;
    case 'Button':
      return <ButtonWidget definition={definition} onAction={onAction} />;
    case 'Box':
      return <BoxWidget definition={definition} />;
    default:
      console.warn(`Unknown widget type: ${definition.type}`);
      return null;
  }
};

const CardWidget: React.FC<{ definition: WidgetDefinition; onAction: WidgetActionHandler }> = ({ definition, onAction }) => {
  const { size, status, children, onClickAction, radius } = definition;
  const sizeClasses: Record<string, string> = {
    sm: 'max-w-sm',
    md: 'max-w-md',
    lg: 'max-w-3xl',
    full: 'w-full',
  };

  const cardClasses = [
    'bg-[#1e1e1e] border border-gray-700 rounded-lg p-4 shadow-sm',
    typeof size === 'string' && sizeClasses[size] ? sizeClasses[size] : 'max-w-3xl',
    radius && typeof radius === 'string' && radiusClasses[radius] ? radiusClasses[radius] : '',
    onClickAction ? 'cursor-pointer transition-colors hover:border-gray-500' : '',
  ]
    .filter(Boolean)
    .join(' ');

  const handleClick = () => {
    if (onClickAction) {
      onAction(onClickAction);
    }
  };

  return (
    <div className={cardClasses} onClick={handleClick} role={onClickAction ? 'button' : undefined} tabIndex={onClickAction ? 0 : undefined}>
      {status && (
        <div className="flex items-center gap-2 mb-3">
          {renderIcon(status.icon, 'w-3.5 h-3.5 text-green-400')}
          <span className="text-xs font-medium text-green-300 bg-green-400/10 px-2 py-1 rounded-full uppercase tracking-wide">
            {status.text}
          </span>
        </div>
      )}
      {renderChildren(children, onAction)}
    </div>
  );
};

const ListViewWidget: React.FC<{ definition: WidgetDefinition; onAction: WidgetActionHandler }> = ({ definition, onAction }) => {
  const { children, limit, gap } = definition;
  const items = limit ? children?.slice(0, limit) : children;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: gap !== undefined ? gap * GAP_MULTIPLIER : undefined }}>
      {renderChildren(items, onAction)}
    </div>
  );
};

const ListViewItemWidget: React.FC<{ definition: WidgetDefinition; onAction: WidgetActionHandler }> = ({ definition, onAction }) => {
  const { children, onClickAction, align, gap, justify } = definition;
  const style: React.CSSProperties = {
    cursor: onClickAction ? 'pointer' : undefined,
    alignItems: alignToCss(align),
    justifyContent: justifyToCss(justify),
    gap: gap !== undefined ? gap * GAP_MULTIPLIER : undefined,
  };

  return (
    <div
      className="flex border-b border-gray-800 last:border-0 py-2"
      style={{ ...style, flexDirection: 'row' }}
      onClick={() => onClickAction && onAction(onClickAction)}
    >
      {renderChildren(children, onAction)}
    </div>
  );
};

const TitleWidget: React.FC<{ definition: WidgetDefinition }> = ({ definition }) => {
  const { value, size = 'lg', weight = 'semibold', color } = definition;
  const sizeClass = typeof size === 'string' && textSizeClasses[size] ? textSizeClasses[size] : textSizeClasses.lg;
  const weightClass: Record<string, string> = {
    normal: 'font-normal',
    medium: 'font-medium',
    semibold: 'font-semibold',
    bold: 'font-bold',
  };
  const colorClass = color && typeof color === 'string' && textColorClasses[color] ? textColorClasses[color] : 'text-white';

  return <h3 className={[sizeClass, weightClass[weight] ?? 'font-semibold', colorClass].join(' ')}>{value}</h3>;
};

const DividerWidget: React.FC<{ definition: WidgetDefinition }> = ({ definition }) => {
  const { spacing } = definition;
  const marginValue = spacing !== undefined ? spacing : 12;

  return <hr className="border-gray-800" style={{ marginTop: marginValue, marginBottom: marginValue }} />;
};

const TextWidget: React.FC<{ definition: WidgetDefinition }> = ({ definition }) => {
  const { value, size = 'sm', weight = 'normal', color, maxLines } = definition;
  const sizeClass = typeof size === 'string' && textSizeClasses[size] ? textSizeClasses[size] : textSizeClasses.sm;
  const weightClass: Record<string, string> = {
    normal: 'font-normal',
    medium: 'font-medium',
    semibold: 'font-semibold',
    bold: 'font-bold',
  };
  const colorClass = color && typeof color === 'string' && textColorClasses[color] ? textColorClasses[color] : 'text-gray-200';
  const style: React.CSSProperties = {};

  if (maxLines && Number(maxLines) > 0) {
    style.display = '-webkit-box';
    style.WebkitLineClamp = Number(maxLines);
    style.WebkitBoxOrient = 'vertical';
    style.overflow = 'hidden';
  }

  return (
    <p className={[sizeClass, weightClass[weight] ?? 'font-normal', colorClass].join(' ')} style={style}>
      {value}
    </p>
  );
};

const CaptionWidget: React.FC<{ definition: WidgetDefinition }> = ({ definition }) => {
  const { value, size = 'sm', color = 'secondary', weight } = definition;
  const sizeClass = typeof size === 'string' && textSizeClasses[size] ? textSizeClasses[size] : textSizeClasses.xs;
  const colorClass = color && typeof color === 'string' && textColorClasses[color] ? textColorClasses[color] : 'text-gray-400';
  const weightClass: Record<string, string> = {
    normal: 'font-normal',
    medium: 'font-medium',
    semibold: 'font-semibold',
    bold: 'font-bold',
  };

  return <p className={[sizeClass, colorClass, weight ? weightClass[weight] ?? '' : ''].filter(Boolean).join(' ')}>{value}</p>;
};

const BadgeWidget: React.FC<{ definition: WidgetDefinition }> = ({ definition }) => {
  const { label, value, color, variant = 'soft', size = 'sm' } = definition;
  const badgeSizeClasses: Record<string, string> = {
    xs: 'text-xs px-2 py-0.5',
    sm: 'text-xs px-2.5 py-0.5',
    md: 'text-sm px-3 py-1',
  };
  const colorKey = typeof color === 'string' ? color.toLowerCase() : 'neutral';
  const softClass = badgeColorClasses[colorKey] ?? badgeColorClasses.neutral;

  let variantClass = 'border border-gray-600 text-gray-200';
  if (variant === 'soft') {
    variantClass = softClass;
  } else if (variant === 'solid') {
    variantClass = 'bg-blue-500 text-white border-blue-500';
  } else if (variant === 'outline') {
    variantClass = 'border border-gray-500 text-gray-200';
  } else if (variant === 'ghost') {
    variantClass = 'text-gray-200';
  }

  const className = ['inline-flex items-center font-semibold rounded-full', badgeSizeClasses[typeof size === 'string' ? size : 'sm'] ?? badgeSizeClasses.sm, variantClass]
    .filter(Boolean)
    .join(' ');

  return <span className={className}>{label ?? value}</span>;
};

const ImageWidget: React.FC<{ definition: WidgetDefinition }> = ({ definition }) => {
  const { src, alt, aspectRatio, radius, frame } = definition;
  const style: React.CSSProperties = {};

  if (aspectRatio) {
    const ratio = typeof aspectRatio === 'number' ? aspectRatio : aspectRatio.toString().replace(':', ' / ');
    style.aspectRatio = ratio;
  }

  const classes = [
    'w-full h-auto object-cover',
    radius && typeof radius === 'string' && radiusClasses[radius] ? radiusClasses[radius] : 'rounded-lg',
    frame ? 'border border-gray-700' : '',
  ]
    .filter(Boolean)
    .join(' ');

  return (
    <div className="overflow-hidden">
      <img src={src} alt={alt || 'Widget image'} className={classes} style={style} />
    </div>
  );
};

const RowWidget: React.FC<{ definition: WidgetDefinition; onAction: WidgetActionHandler }> = ({ definition, onAction }) => {
  const { children, align, justify, gap, wrap, flex, onClickAction } = definition;
  const style: React.CSSProperties = {
    display: 'flex',
    flexDirection: 'row',
    alignItems: alignToCss(align),
    justifyContent: justifyToCss(justify),
    gap: gap !== undefined ? gap * GAP_MULTIPLIER : undefined,
    flexWrap: wrap ? 'wrap' : undefined,
    flex: typeof flex === 'number' ? flex : undefined,
    cursor: onClickAction ? 'pointer' : undefined,
  };

  return (
    <div
      style={style}
      onClick={() => onClickAction && onAction(onClickAction)}
      role={onClickAction ? 'button' : undefined}
      tabIndex={onClickAction ? 0 : undefined}
    >
      {renderChildren(children, onAction)}
    </div>
  );
};

const ColWidget: React.FC<{ definition: WidgetDefinition; onAction: WidgetActionHandler }> = ({ definition, onAction }) => {
  const { children, align, justify, gap, flex } = definition;
  const style: React.CSSProperties = {
    display: 'flex',
    flexDirection: 'column',
    alignItems: alignToCss(align),
    justifyContent: justifyToCss(justify),
    gap: gap !== undefined ? gap * GAP_MULTIPLIER : undefined,
    flex: typeof flex === 'number' ? flex : undefined,
  };

  return <div style={style}>{renderChildren(children, onAction)}</div>;
};

const SpacerWidget: React.FC<{ definition: WidgetDefinition }> = ({ definition }) => {
  const { flex } = definition;
  return <div style={{ flex: typeof flex === 'number' ? flex : 1 }} />;
};

const ButtonWidget: React.FC<{ definition: WidgetDefinition; onAction: WidgetActionHandler }> = ({ definition, onAction }) => {
  const { label, value, variant, color, size, pill, iconStart, onClickAction } = definition;
  const classes = buttonVariantClasses(variant, typeof color === 'string' ? color : undefined, typeof size === 'string' ? size : 'sm', Boolean(pill));
  const Icon = iconStart ? iconRegistry[iconStart] || iconRegistry[iconStart.toLowerCase?.() ?? ''] : undefined;

  return (
    <button type="button" className={classes} onClick={() => onClickAction && onAction(onClickAction)}>
      {Icon && <Icon className="w-3.5 h-3.5" />}
      <span>{label ?? value}</span>
    </button>
  );
};

const BoxWidget: React.FC<{ definition: WidgetDefinition }> = ({ definition }) => {
  const { background, size, radius = 'full' } = definition;
  const dimension = typeof size === 'number' ? size : 10;
  const classes = ['inline-flex shrink-0', radius && typeof radius === 'string' && radiusClasses[radius] ? radiusClasses[radius] : 'rounded-full', 'border border-transparent']
    .filter(Boolean)
    .join(' ');

  return <span className={classes} style={{ width: `${dimension}px`, height: `${dimension}px`, backgroundColor: typeof background === 'string' ? background : '#6b7280' }} />;
};

const renderChildren = (children: WidgetDefinition[] | undefined, onAction: WidgetActionHandler) => {
  if (!children || children.length === 0) {
    return null;
  }

  return children.map((child, idx) => <WidgetComponent key={`${child.type}-${idx}`} definition={child} onAction={onAction} />);
};

const renderIcon = (icon?: string, className?: string) => {
  if (!icon) {
    return null;
  }

  const IconComponent = iconRegistry[icon] || iconRegistry[icon.toLowerCase?.() ?? ''];
  if (!IconComponent) {
    return null;
  }

  return <IconComponent className={className} />;
};
