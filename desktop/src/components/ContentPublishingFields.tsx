import { Pin } from 'lucide-react';
import { contentLifecycleFor, type DocumentStateInput } from '../lib/contentLifecycle';
import type { ContentKind } from '../types';
import { Select } from './ds/Select';

type ContentPublishingFieldsProps = {
  kind: ContentKind;
  value: DocumentStateInput;
  disabled?: boolean;
  onChange: (value: DocumentStateInput) => void;
};

type StateOption = {
  value: string;
  label: string;
};

const uniqueOptions = (options: StateOption[]) => options.filter((option, index) => (
  options.findIndex((candidate) => candidate.value === option.value) === index
));

export function ContentPublishingFields({
  kind,
  value,
  disabled = false,
  onChange,
}: ContentPublishingFieldsProps) {
  const lifecycle = contentLifecycleFor(kind, value.status, value.visibility);
  const statusOptions = uniqueOptions([
    { value: lifecycle.status, label: lifecycle.statusLabel },
    ...lifecycle.actions
      .filter((action) => action.group === 'status')
      .map((action) => ({
        value: action.nextState.status,
        label: contentLifecycleFor(kind, action.nextState.status, value.visibility).statusLabel,
      })),
  ]);
  const visibilityOptions = uniqueOptions([
    { value: lifecycle.visibility, label: lifecycle.visibilityLabel },
    ...lifecycle.actions
      .filter((action) => action.group === 'visibility')
      .map((action) => ({
        value: action.nextState.visibility,
        label: contentLifecycleFor(kind, value.status, action.nextState.visibility).visibilityLabel,
      })),
  ]);

  return (
    <div className="content-publishing-fields">
      <div className="content-settings-control">
        <span>Lifecycle</span>
        <small>Where this work currently sits in its own process.</small>
        <Select
          aria-label="Lifecycle status"
          value={value.status}
          disabled={disabled}
          onChange={(event) => onChange({ ...value, status: event.target.value })}
        >
          {statusOptions.map((option) => (
            <option key={option.value} value={option.value}>{option.label}</option>
          ))}
        </Select>
      </div>

      <div className="content-settings-control">
        <span>Visibility</span>
        <small>Who can discover the content after the next deployment.</small>
        <Select
          aria-label="Content visibility"
          value={value.visibility}
          disabled={disabled || visibilityOptions.length === 1}
          onChange={(event) => onChange({ ...value, visibility: event.target.value })}
        >
          {visibilityOptions.map((option) => (
            <option key={option.value} value={option.value}>{option.label}</option>
          ))}
        </Select>
      </div>

      {kind === 'moment' && (
        <label className="content-publishing-pin">
          <input
            type="checkbox"
            checked={Boolean(value.pinned)}
            disabled={disabled}
            onChange={(event) => onChange({ ...value, pinned: event.target.checked })}
          />
          <span className="content-publishing-switch" aria-hidden="true"><i /></span>
          <span className="content-publishing-pin-copy">
            <strong><Pin size={14} aria-hidden="true" /> Pin to top</strong>
            <small>Keep this moment above newer timeline entries.</small>
          </span>
        </label>
      )}
    </div>
  );
}
