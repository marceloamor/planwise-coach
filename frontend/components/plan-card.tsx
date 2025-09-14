/**
 * Plan Card Component
 * Displays the current training plan with weeks and sessions
 */

import { PlanDoc, Session, WeekPlan } from "@/app/api";

interface PlanCardProps {
  plan: PlanDoc;
  version?: number;
  updatedAt?: string;
}

function SessionRow({ session }: { session: Session }) {
  const parts: string[] = [];
  
  // Session type (always shown)
  parts.push(`**${session.type}**`);
  
  // Distance or time
  if (session.distance_km != null) {
    parts.push(`${session.distance_km} km`);
  } else if (session.time_min != null) {
    parts.push(`${session.time_min} min`);
  }
  
  // Intensity
  if (session.intensity) {
    parts.push(`${session.intensity}`);
  }
  
  // RPE
  if (session.rpe != null) {
    parts.push(`RPE ${session.rpe}`);
  }
  
  // Structure (workout details)
  if (session.structure) {
    parts.push(`· ${session.structure}`);
  }
  
  // Notes
  if (session.notes) {
    parts.push(`— ${session.notes}`);
  }
  
  // Day of week
  const dayLabel = session.day_of_week 
    ? `(${session.day_of_week.charAt(0).toUpperCase() + session.day_of_week.slice(1)})` 
    : '';
  
  return (
    <li className="session-item">
      <span className="session-content">
        {parts.join(' · ')} {dayLabel}
      </span>
    </li>
  );
}

function WeekSection({ weekKey, week }: { weekKey: string; week: WeekPlan }) {
  const weekNumber = weekKey.replace('week_', '').replace('_', ' ');
  const weekTitle = `Week ${weekNumber.toUpperCase()}`;
  
  return (
    <div className="week-section">
      <h3 className="week-title">
        {weekTitle}
        {week.mileage_target && (
          <span className="mileage-target"> · {week.mileage_target} km</span>
        )}
      </h3>
      
      <ul className="sessions-list">
        {week.sessions.map((session, index) => (
          <SessionRow key={index} session={session} />
        ))}
      </ul>
    </div>
  );
}

export function PlanCard({ plan, version, updatedAt }: PlanCardProps) {
  // Sort weeks chronologically
  const weeks = Object.entries(plan.weeks).sort(([a], [b]) => a.localeCompare(b));
  
  return (
    <section className="plan-card">
      <div className="plan-header">
        <h2>Current Training Plan</h2>
        {version && (
          <span className="plan-version">v{version}</span>
        )}
      </div>
      
      <div className="plan-meta">
        <div className="meta-row">
          <span className="meta-label">Goal:</span>
          <span className="meta-value">{plan.meta.goal || "—"}</span>
        </div>
        
        {plan.meta.race_date && (
          <div className="meta-row">
            <span className="meta-label">Race Date:</span>
            <span className="meta-value">{plan.meta.race_date}</span>
          </div>
        )}
        
        <div className="meta-row">
          <span className="meta-label">Phase:</span>
          <span className="meta-value">{plan.meta.phase || "—"}</span>
        </div>
        
        {plan.meta.weekly_km_target && (
          <div className="meta-row">
            <span className="meta-label">Weekly Target:</span>
            <span className="meta-value">{plan.meta.weekly_km_target} km</span>
          </div>
        )}
        
        {plan.constraints && (
          <>
            <div className="meta-row">
              <span className="meta-label">Max Weekly Increase:</span>
              <span className="meta-value">{plan.constraints.max_weekly_increase_pct}%</span>
            </div>
            <div className="meta-row">
              <span className="meta-label">Min Rest Days:</span>
              <span className="meta-value">{plan.constraints.min_rest_days}</span>
            </div>
          </>
        )}
      </div>
      
      <div className="weeks-container">
        {weeks.map(([weekKey, week]) => (
          <WeekSection key={weekKey} weekKey={weekKey} week={week} />
        ))}
      </div>
      
      {updatedAt && (
        <div className="plan-footer">
          <small className="update-time">
            Updated: {new Date(updatedAt).toLocaleString()}
          </small>
        </div>
      )}
      
      <style jsx>{`
        .plan-card {
          border: 1px solid #e5e7eb;
          border-radius: 8px;
          padding: 1.5rem;
          margin-top: 1.5rem;
          background: white;
          box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        }
        
        .plan-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 1rem;
          border-bottom: 1px solid #f3f4f6;
          padding-bottom: 0.5rem;
        }
        
        .plan-header h2 {
          margin: 0;
          color: #1f2937;
          font-size: 1.25rem;
          font-weight: 600;
        }
        
        .plan-version {
          background: #f3f4f6;
          color: #6b7280;
          padding: 0.25rem 0.5rem;
          border-radius: 4px;
          font-size: 0.75rem;
          font-weight: 500;
        }
        
        .plan-meta {
          margin-bottom: 1.5rem;
          padding: 1rem;
          background: #f9fafb;
          border-radius: 6px;
        }
        
        .meta-row {
          display: flex;
          justify-content: space-between;
          margin-bottom: 0.5rem;
        }
        
        .meta-row:last-child {
          margin-bottom: 0;
        }
        
        .meta-label {
          color: #6b7280;
          font-weight: 500;
        }
        
        .meta-value {
          color: #1f2937;
          font-weight: 600;
        }
        
        .weeks-container {
          space-y: 1.5rem;
        }
        
        .week-section {
          margin-bottom: 1.5rem;
        }
        
        .week-title {
          margin: 0 0 0.75rem 0;
          color: #1f2937;
          font-size: 1.1rem;
          font-weight: 600;
        }
        
        .mileage-target {
          color: #059669;
          font-weight: 500;
        }
        
        .sessions-list {
          margin: 0;
          padding-left: 1.25rem;
          list-style: none;
        }
        
        .session-item {
          margin-bottom: 0.5rem;
          position: relative;
        }
        
        .session-item::before {
          content: "•";
          color: #6b7280;
          position: absolute;
          left: -1rem;
        }
        
        .session-content {
          color: #374151;
          line-height: 1.5;
        }
        
        .plan-footer {
          margin-top: 1.5rem;
          padding-top: 1rem;
          border-top: 1px solid #f3f4f6;
          text-align: center;
        }
        
        .update-time {
          color: #9ca3af;
        }
      `}</style>
    </section>
  );
} 