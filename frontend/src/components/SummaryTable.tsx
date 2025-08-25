import React from 'react';
import { SummaryTable as SummaryTableType } from '../types/dashboard';

interface SummaryTableProps {
  data: SummaryTableType;
}

export const SummaryTable: React.FC<SummaryTableProps> = ({ data }) => {
  return (
    <div className="card" data-testid="summary-table">
      <div className="card-header">
        <h3 className="card-title">Key Metrics</h3>
      </div>
      
      <table className="table">
        <tbody>
          {data.rows.map((row) => (
            <tr key={row.key}>
              <td style={{ width: '40%', color: 'var(--text-secondary)' }}>
                {row.label}
                {row.tooltip && (
                  <span 
                    title={row.tooltip} 
                    style={{ 
                      marginLeft: '4px', 
                      cursor: 'help',
                      opacity: 0.5
                    }}
                  >
                    ⓘ
                  </span>
                )}
              </td>
              <td style={{ fontWeight: '600' }}>
                {row.value_formatted}
              </td>
              {row.delta_formatted && (
                <td style={{ 
                  textAlign: 'right',
                  color: row.delta_pct && row.delta_pct > 0 ? 'var(--accent-secondary)' : 'var(--accent-danger)'
                }}>
                  {row.delta_pct && row.delta_pct > 0 ? '▲' : '▼'} {row.delta_formatted}
                </td>
              )}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};